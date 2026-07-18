import os
import re
import json
import random
from typing import Optional

import psycopg2
import psycopg2.extras

# Postgres-backed persistence: one row per shareable portfolio link.
# Replaces the old flat-file JSON storage, which lived on Render's local
# disk and got wiped on every restart/redeploy. A real DB survives that.
# Still deliberately simple — no accounts, no auth, no editing.

DATABASE_URL = os.environ.get("DATABASE_URL")


def _get_conn():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to your .env locally and to "
            "Render's environment variables."
        )
    return psycopg2.connect(DATABASE_URL)


def init_db() -> None:
    """
    Creates the portfolios table if it doesn't exist yet. Call this once
    on app startup so a fresh database is ready without a manual step.
    """
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS portfolios (
                    slug TEXT PRIMARY KEY,
                    profile JSONB NOT NULL,
                    theme TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        conn.commit()


def _slugify(name: str) -> str:
    """
    Turns a person's name into a URL-safe slug.
    """
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "portfolio"


def _slug_exists(slug: str) -> bool:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM portfolios WHERE slug = %s", (slug,))
            return cur.fetchone() is not None


def generate_slug(name: str) -> str:
    """
    Builds a slug from a person's name. If that slug is already taken
    (e.g. two people named 'Aryan Mehta'), appends a random 4-digit
    suffix and retries until a free slug is found.
    """
    base_slug = _slugify(name)
    slug = base_slug
    attempts = 0
    while _slug_exists(slug) and attempts < 20:
        slug = f"{base_slug}-{random.randint(1000, 9999)}"
        attempts += 1
    return slug


def save_portfolio(slug: str, profile_dict: dict, theme: str) -> None:
    """
    Persists a chosen profile + theme under a slug so it can be
    revisited later at a stable link. Upserts, so re-finalizing the
    same slug just updates it instead of failing.
    """
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO portfolios (slug, profile, theme)
                VALUES (%s, %s, %s)
                ON CONFLICT (slug) DO UPDATE
                SET profile = EXCLUDED.profile, theme = EXCLUDED.theme
                """,
                (slug, json.dumps(profile_dict), theme),
            )
        conn.commit()


def load_portfolio(slug: str) -> Optional[dict]:
    """
    Loads a previously saved {profile, theme} record, or None if
    no portfolio exists at that slug.
    """
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT profile, theme FROM portfolios WHERE slug = %s", (slug,)
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {"profile": row["profile"], "theme": row["theme"]}