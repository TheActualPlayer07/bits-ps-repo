// lib/guards.ts
//
// Two best-effort guards for a serverless environment:
//
// 1. A content-hash cache: identical (code, language) pairs skip the LLM
//    calls entirely and return the prior verdict, which also happens to be
//    how we guarantee "same code -> same score every run".
// 2. A per-IP token-bucket rate limiter, to stop one submitter from hammering
//    back-to-back requests and burning through API quota.
//
// IMPORTANT / HONEST CAVEAT: both live in a module-level Map, which only
// persists for the life of a single warm serverless instance. Vercel can and
// will spin up multiple instances under real concurrent load, each with its
// own Map, so this is NOT a distributed cache or a hard rate limit. It's
// enough to dedupe within a session and take the edge off a burst from one
// instance. For a real multi-instance guarantee, swap this for Vercel KV or
// Upstash Redis (a few lines of change, see README).

import { createHash } from "crypto";

const CACHE_MAX_ENTRIES = 200;
const cache = new Map<string, unknown>();

export function hashKey(code: string, language: string): string {
  return createHash("sha256").update(`${language}::${code}`).digest("hex");
}

export function getCached<T>(key: string): T | undefined {
  return cache.get(key) as T | undefined;
}

export function setCached<T>(key: string, value: T): void {
  if (cache.size >= CACHE_MAX_ENTRIES) {
    const oldest = cache.keys().next().value;
    if (oldest !== undefined) cache.delete(oldest);
  }
  cache.set(key, value);
}

interface Bucket {
  tokens: number;
  lastRefill: number;
}

const BUCKET_CAPACITY = 8; // max burst
const REFILL_PER_MS = 5 / 60_000; // 5 requests/minute steady state
const buckets = new Map<string, Bucket>();

export function checkRateLimit(ip: string): { allowed: boolean; retryAfterMs?: number } {
  const now = Date.now();
  const bucket = buckets.get(ip) ?? { tokens: BUCKET_CAPACITY, lastRefill: now };

  const elapsed = now - bucket.lastRefill;
  bucket.tokens = Math.min(BUCKET_CAPACITY, bucket.tokens + elapsed * REFILL_PER_MS);
  bucket.lastRefill = now;

  if (bucket.tokens < 1) {
    buckets.set(ip, bucket);
    const msPerToken = 1 / REFILL_PER_MS;
    return { allowed: false, retryAfterMs: Math.ceil(msPerToken * (1 - bucket.tokens)) };
  }

  bucket.tokens -= 1;
  buckets.set(ip, bucket);
  return { allowed: true };
}
