import * as cheerio from "cheerio";
import {
  ResearchData,
  ResearchDataSchema,
  researchJsonSchema,
} from "../types";
import {
  generateGroundedText,
  generateStructured,
  isSearchGroundingEnabled,
} from "../gemini";

const MAX_PAGE_TEXT_CHARS = 40000;

interface FetchResult {
  title: string;
  text: string;
  links: { label: string; path: string }[];
}

/**
 * Fetches the company's own URL, extracts readable text copy, and harvests 
 * a structural map of real, verified hyperlinks found on the page.
 */
async function fetchPageText(url: string): Promise<FetchResult> {
  const res = await fetch(url, {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (compatible; HeroPageGeneratorBot/1.0; +https://github.com/)",
    },
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    throw new Error(`Could not fetch ${url} (HTTP ${res.status}). Check the URL is correct and public.`);
  }

  const html = await res.text();
  const $ = cheerio.load(html);

  // Harvest up to 40 unique internal links before stripping the document clean
  const harvestedLinks: { label: string; path: string }[] = [];
  $("a[href]").each((_, el) => {
    const href = $(el).attr("href")?.trim();
    const text = $(el).text().replace(/\s+/g, " ").trim();
    
    if (href && text && text.length > 2 && !href.startsWith("#") && !href.startsWith("javascript:")) {
      if (harvestedLinks.length < 40 && !harvestedLinks.some(item => item.path === href)) {
        harvestedLinks.push({ label: text, path: href });
      }
    }
  });

  // Clear out heavy code scripts and non-copy structures
  $("script, style, noscript, svg, iframe").remove();

  const title = $("title").first().text().trim();
  const metaDescription = $('meta[name="description"]').attr("content") || "";

  const bodyText = $("body")
    .text()
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, MAX_PAGE_TEXT_CHARS);

  const linksMapText = harvestedLinks
    .map(link => `- Link Option -> Element Label: "${link.label}" maps to exact URL path: ${link.path}`)
    .join("\n");

  return {
    title,
    text: `Title: ${title}\nMeta description: ${metaDescription}\n\n=== VERIFIED REAL HYPERLINKS ON THIS PAGE ===\n${linksMapText || "(None extracted)"}\n\n=== MAIN BODY COPY ===\n${bodyText}`,
    links: harvestedLinks
  };
}

/**
 * Optional second pass: ask Gemini (with Google Search grounding) what it
 * can find about the company beyond its own site.
 */
async function fetchOutsideContext(companyUrl: string, siteTitle: string, modelName?: string): Promise<string> {
  if (!isSearchGroundingEnabled()) return "";

  try {
    const prompt = `Search for independent, third-party information about the company behind this website: ${companyUrl} (page title: "${siteTitle}"). Summarize in plain text: what reviewers/press say about it, who its customers seem to be, and any concrete facts (funding, size, notable clients, launch date) that wouldn't come from the company's own marketing copy. If you find nothing reliable, say so plainly.`;
    return await generateGroundedText(prompt, modelName);
  } catch {
    return "";
  }
}

export async function runResearch(url: string, modelName?: string): Promise<ResearchData> {
  const normalizedUrl = /^https?:\/\//i.test(url) ? url : `https://${url}`;

  const { title, text: siteText, links: harvestedLinks } = await fetchPageText(normalizedUrl);
  const outsideContext = await fetchOutsideContext(normalizedUrl, title, modelName);

  const prompt = `You are researching a company from its own website and (if available) outside context, in order to later write a landing page about it. Extract only what's actually supported by the material below — never invent products, numbers, or claims that aren't there.

=== COMPANY WEBSITE (${normalizedUrl}) ===
${siteText}

=== OUTSIDE CONTEXT (may be empty) ===
${outsideContext || "(no outside context available)"}

Fill in the research record now.`;

  const raw = await generateStructured<ResearchData>({
    systemInstruction:
      "You are a meticulous research analyst. You extract only facts and claims that are actually present in the supplied material. You never invent statistics, customer names, or claims. When information is genuinely absent, you say so plainly instead of guessing.",
    prompt,
    jsonSchema: researchJsonSchema,
    model: modelName,
  });

  // FIX: Inject the harvested links directly into notableDetails so they survive schema filtering
  // and pass seamlessly to positioning and copywriting steps.
  const linkContextStrings = harvestedLinks.map(
    link => `REAL SITE DEEP LINK OPTION: Text "${link.label}" goes to exact path "${link.path}"`
  );

  const parsed = ResearchDataSchema.safeParse({ 
    ...raw, 
    url: normalizedUrl,
    notableDetails: [...(raw.notableDetails || []), ...linkContextStrings] // ◄ Safe programmatic injection payload
  });

  if (!parsed.success) {
    throw new Error(`Research step returned malformed data: ${parsed.error.message}`);
  }
  return parsed.data;
}
