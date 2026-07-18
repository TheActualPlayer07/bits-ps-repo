import pandas as pd

def parse_excel_input(file_object):
    """
    Parses the uploaded Excel file to extract job preferences, skills, or LinkedIn URL.
    Returns a dictionary with extracted information.
    """
    try:
        # Read the excel file
        df = pd.read_excel(file_object)
        
        # We assume the excel file might have columns like 'Skill', 'Preference', 'LinkedIn URL'
        # Let's extract them dynamically into a dictionary
        extracted_data = {}
        
        # Simple extraction logic: convert dataframe to list of records
        extracted_data["records"] = df.to_dict(orient="records")
        extracted_data["columns"] = df.columns.tolist()
        
        return {
            "success": True,
            "data": extracted_data,
            "message": "Excel file parsed successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to parse Excel file."
        }

def parse_text_input(text_input):
    """
    Parses direct text input such as a LinkedIn URL or a comma-separated list of skills.
    """
    if not text_input:
        return {"success": False, "message": "Input is empty."}
        
    text = text_input.strip()
    is_url = text.startswith("http://") or text.startswith("https://")
    
    return {
        "success": True,
        "is_url": is_url,
        "data": text,
        "message": "Text input parsed."
    }
