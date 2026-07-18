import json
from src.input_module import parse_text_input
from src.pipeline import run_basic_pipeline

def main():
    print("--- Testing Phase 1 & Phase 2 Pipeline ---")
    
    # 1. Simulate user input (Text Skills)
    user_input = "I am a Data Scientist with skills in Python, SQL, and Machine Learning."
    parsed_input = parse_text_input(user_input)
    print("\n[Input Parsed Successfully]")
    print("User Text:", parsed_input["data"])
    
    # 2. Run Pipeline (No API Key first to simulate Phase 1)
    print("\n--- Running Phase 1 (Matching Only) ---")
    result_phase1 = run_basic_pipeline(parsed_input)
    print("Status:", result_phase1["status"])
    print("Message:", result_phase1["message"])
    print(f"Jobs Matched: {len(result_phase1['jobs'])}")
    for j in result_phase1["jobs"]:
        print(f" - {j['title']} at {j['company']}")

    # 3. We cannot test Phase 2 insights without a real API key, so we'll just demonstrate it.
    print("\n--- Phase 2 Note ---")
    print("If an OpenAI API key was provided, the pipeline would generate insights like 'Role Fit', 'Skills to Gain', 'Work Culture', and 'Career Path' for the jobs above.")
    print("------------------------------------------")

if __name__ == "__main__":
    main()
