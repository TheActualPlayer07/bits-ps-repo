import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

from core.parser import get_raw_resume_text
from core.schema import PortfolioProfile

load_dotenv()


def generate_portfolio_data(raw_text: str) -> PortfolioProfile:
    """
    Sends raw resume text to Gemini and forces it into the PortfolioProfile schema.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY inside your .env configuration file.")

    client = genai.Client(api_key=api_key)

    safety_settings = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
    ]

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]

    system_instruction = (
        "You are an expert technical ghostwriter and portfolio engineer. "
        "Your task is to review raw resume text and upgrade it into an impactful portfolio profile. "
        "Enhance dull bullet points into professional highlights following an active verb structure. "
        "Draft a compelling personal biography. Create a modern tech headline. "
        "CRITICAL: Do not invent or hallucinate facts, companies, or skills that do not exist in the text."
    )

    for model_name in models_to_try:
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=PortfolioProfile,
                safety_settings=safety_settings,
            )

            response = client.models.generate_content(
                model=model_name,
                contents=raw_text,
                config=config,
            )

            return response.parsed

        except APIError as e:
            print(f"Model {model_name} failed: {e}")

    raise RuntimeError("All Gemini model fallbacks failed.")


if __name__ == "__main__":
    test_file = "samples/test_resume.pdf"

    print("--- Initiating Step 2 AI Pipeline Run ---")

    try:
        print("Reading file text via Step 1 parser...")
        extracted_text = get_raw_resume_text(test_file)

        print("Transmitting to Gemini Pipeline...")
        structured_output = generate_portfolio_data(extracted_text)

        print("\n[SUCCESS] AI Extraction complete!")
        print(f"Generated Profile for: {structured_output.name}")
        print(f"AI Headline: {structured_output.headline}")
        print(f"Parsed Skills Count: {len(structured_output.skills)}")

    except Exception as e:
        print(f"\n[CRITICAL FAILURE] Pipeline execution failed: {e}")