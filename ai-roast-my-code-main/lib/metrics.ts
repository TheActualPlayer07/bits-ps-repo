// lib/metrics.ts
//
// Lightweight, language-aware static analysis. This isn't a full AST parser
// (that would need per-language toolchains we can't ship in a single
// serverless function), but it plays the same role the work order describes:
// strip non-semantic noise before the code hits the LLM, and hand the model
// hard numbers instead of asking it to eyeball everything from raw text.

export type Language =
  | "python"
  | "javascript"
  | "typescript"
  | "java"
  | "cpp"
  | "c"
  | "go"
  | "rust"
  | "other";

export interface CodeMetrics {
  language: Language;
  totalLines: number;
  codeLines: number;
  commentLines: number;
  blankLines: number;
  commentRatio: number;
  functionCount: number;
  maxNestingDepth: number;
  avgLineLength: number;
  longestLine: number;
  approxCyclomaticComplexity: number;
  strippedCode: string;
  tokenReductionPct: number;
}

const COMMENT_PATTERNS: Record<Language, { line: RegExp[]; blockStart?: RegExp; blockEnd?: RegExp }> = {
  python: { line: [/^\s*#/] },
  javascript: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  typescript: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  java: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  cpp: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  c: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  go: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  rust: { line: [/^\s*\/\//], blockStart: /\/\*/, blockEnd: /\*\// },
  other: { line: [/^\s*(#|\/\/)/] },
};

const FUNCTION_PATTERNS: Record<Language, RegExp> = {
  python: /^\s*(async\s+)?def\s+\w+\s*\(/,
  javascript: /\b(function\s+\w+\s*\(|=>\s*{|=\s*function\s*\()/,
  typescript: /\b(function\s+\w+\s*\(|=>\s*{|=\s*function\s*\()/,
  java: /\b(public|private|protected|static)\b[^;{]*\([^)]*\)\s*{/,
  cpp: /\w[\w:<>~]*\s+\w+\s*\([^;{]*\)\s*{/,
  c: /\w[\w:<>~]*\s+\w+\s*\([^;{]*\)\s*{/,
  go: /^\s*func\s+/,
  rust: /^\s*(pub\s+)?(async\s+)?fn\s+\w+/,
  other: /\b(function|def|fn)\b/,
};

const DECISION_KEYWORDS =
  /\b(if|elif|else if|for|while|case|catch|except|&&|\|\||\?\?|switch)\b/g;

export function detectLanguage(input: string): Language {
  return (input?.toLowerCase() as Language) in COMMENT_PATTERNS
    ? (input.toLowerCase() as Language)
    : "other";
}

export function analyzeCode(rawCode: string, language: Language): CodeMetrics {
  const lines = rawCode.replace(/\r\n/g, "\n").split("\n");
  const { line: lineCommentPatterns, blockStart, blockEnd } = COMMENT_PATTERNS[language];

  let commentLines = 0;
  let blankLines = 0;
  let inBlockComment = false;
  const keptLines: string[] = [];

  for (const raw of lines) {
    const trimmed = raw.trim();

    if (inBlockComment) {
      commentLines++;
      if (blockEnd && blockEnd.test(raw)) inBlockComment = false;
      continue;
    }
    if (trimmed === "") {
      blankLines++;
      continue;
    }
    if (lineCommentPatterns.some((p) => p.test(raw))) {
      commentLines++;
      continue;
    }
    if (blockStart && blockStart.test(raw) && !(blockEnd && blockEnd.test(raw))) {
      commentLines++;
      inBlockComment = true;
      continue;
    }
    keptLines.push(raw);
  }

  const totalLines = lines.length;
  const codeLines = keptLines.length;
  const commentRatio = totalLines ? commentLines / totalLines : 0;

  const functionPattern = FUNCTION_PATTERNS[language];
  const functionCount = keptLines.filter((l) => functionPattern.test(l)).length;

  // Nesting depth via a simple bracket/indent proxy, whichever the language uses.
  let depth = 0;
  let maxDepth = 0;
  const usesBraces = ["javascript", "typescript", "java", "cpp", "c", "go", "rust", "other"].includes(
    language
  );
  if (usesBraces) {
    for (const l of keptLines) {
      for (const ch of l) {
        if (ch === "{") {
          depth++;
          maxDepth = Math.max(maxDepth, depth);
        } else if (ch === "}") {
          depth = Math.max(0, depth - 1);
        }
      }
    }
  } else {
    // Python-style: indentation width / 4 as a depth proxy.
    for (const l of keptLines) {
      const indent = (l.match(/^\s*/)?.[0].length ?? 0) / 4;
      maxDepth = Math.max(maxDepth, Math.round(indent));
    }
  }

  const lineLengths = keptLines.map((l) => l.length);
  const avgLineLength = lineLengths.length
    ? Math.round(lineLengths.reduce((a, b) => a + b, 0) / lineLengths.length)
    : 0;
  const longestLine = lineLengths.length ? Math.max(...lineLengths) : 0;

  const joined = keptLines.join("\n");
  const decisionMatches = joined.match(DECISION_KEYWORDS) ?? [];
  // +1 baseline path, one branch point per decision keyword.
  const approxCyclomaticComplexity = 1 + decisionMatches.length;

  const strippedCode = keptLines.join("\n");
  const tokenReductionPct = rawCode.length
    ? Math.round(((rawCode.length - strippedCode.length) / rawCode.length) * 100)
    : 0;

  return {
    language,
    totalLines,
    codeLines,
    commentLines,
    blankLines,
    commentRatio: Math.round(commentRatio * 100) / 100,
    functionCount,
    maxNestingDepth: maxDepth,
    avgLineLength,
    longestLine,
    approxCyclomaticComplexity,
    strippedCode,
    tokenReductionPct,
  };
}
