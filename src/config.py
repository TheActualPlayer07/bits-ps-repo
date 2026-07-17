
from groq import Groq
import os
from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:
    st = None

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY and st is not None:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found. Set it in your .env file (local) or Streamlit Secrets (cloud)."
    )

# Default reasoning model
DEFAULT_MODEL = "qwen/qwen3-32b"

# Create one reusable client
client = Groq(api_key=GROQ_API_KEY)


def get_groq_client() -> Groq:
    """Return the shared Groq client."""
    return client