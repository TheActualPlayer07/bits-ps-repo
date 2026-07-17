import { PageContent, PageContentSchema } from "./types";

/**
 * The generated page has no database behind it — the whole PageContent
 * object is packed into the URL itself, so a link is fully self-contained
 * and shareable without any backend storage or expiry.
 */
export function encodePageContent(page: PageContent): string {
  const json = JSON.stringify(page);
  const bytes = new TextEncoder().encode(json);
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary);
}

export function decodePageContent(encoded: string): PageContent {
  const binary = atob(encoded);
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  const json = new TextDecoder().decode(bytes);
  const parsed = PageContentSchema.safeParse(JSON.parse(json));
  if (!parsed.success) {
    throw new Error("This link's page data looks corrupted or was built with an older version.");
  }
  return parsed.data;
}
