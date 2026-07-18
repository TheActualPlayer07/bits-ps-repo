import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

# Import backbone modules and the new multi-theme renderer
from core.parser import get_raw_resume_text
from core.generator import generate_portfolio_data
from core.renderer import render_portfolio_html
from core.schema import PortfolioProfile
from core.storage import generate_slug, save_portfolio, load_portfolio, init_db

app = FastAPI(
    title="Resume to Portfolio Agent API",
    description="Backend engine that transforms raw resumes into structured portfolio profiles with multi-theme support.",
    version="3.1.0"
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def on_startup():
    """
    Creates the portfolios table if it doesn't already exist. Safe to
    run on every boot -- CREATE TABLE IF NOT EXISTS is a no-op once
    the table's there.
    """
    init_db()


@app.get("/")
def read_root():
    """
    Serves the interactive landing page: upload a resume once, then preview
    every available theme rendered with that same structured data.
    """
    return FileResponse("templates/index.html")


@app.post("/api/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    Step 1: Accepts a resume file, runs it through parsing + the Gemini
    narrative pipeline ONCE, and returns the structured profile as JSON.
    The frontend caches this and reuses it to render every theme, so we
    never re-parse or re-call the LLM just to preview a different look.
    """
    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a valid .pdf or .docx file."
        )

    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[WEB] Parsing uploaded file: {file.filename}")
        raw_text = get_raw_resume_text(temp_file_path)

        print("[WEB] Triggering Gemini Narrative Pipeline...")
        structured_portfolio = generate_portfolio_data(raw_text)

        return JSONResponse(content=structured_portfolio.model_dump())

    except Exception as e:
        print(f"[WEB ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"[WEB] Removed temporary file: {temp_file_path}")


@app.post("/api/render", response_class=HTMLResponse)
async def render_theme(
    theme: str = Form(...),
    profile: str = Form(...)  # JSON string of the already-structured PortfolioProfile
):
    """
    Step 2: Renders a single theme from already-structured profile data.
    Called once per theme so the UI can show every template side by side
    without hitting the parser or the LLM again.
    """
    try:
        data = json.loads(profile)
        structured_portfolio = PortfolioProfile(**data)
        html_content = render_portfolio_html(structured_portfolio, theme=theme)
        return HTMLResponse(content=html_content, status_code=200)

    except Exception as e:
        print(f"[WEB ERROR] {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/finalize")
async def finalize_portfolio(
    theme: str = Form(...),
    profile: str = Form(...)  # JSON string of the already-structured PortfolioProfile
):
    """
    Step 3: Persists the chosen theme + profile under a stable, shareable
    slug derived from the person's name. Turns the final pick from a
    one-off response into a durable link others can open directly.
    """
    try:
        data = json.loads(profile)
        structured_portfolio = PortfolioProfile(**data)

        slug = generate_slug(structured_portfolio.name)
        save_portfolio(slug, structured_portfolio.model_dump(), theme)

        return JSONResponse(content={"slug": slug, "url": f"/p/{slug}"})

    except Exception as e:
        print(f"[WEB ERROR] {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/p/{slug}", response_class=HTMLResponse)
async def view_shared_portfolio(slug: str):
    """
    Serves a previously generated portfolio at its stable, shareable link.
    Namespaced under /p/ so it can't shadow other routes or intercept
    unrelated requests like /favicon.ico.
    Re-renders from the stored structured profile (rather than storing raw
    HTML) so shared links stay in sync with whatever the renderer does
    at request time.
    """
    record = load_portfolio(slug)
    if record is None:
        raise HTTPException(status_code=404, detail="No portfolio found at this link.")

    structured_portfolio = PortfolioProfile(**record["profile"])
    html_content = render_portfolio_html(structured_portfolio, theme=record["theme"])
    return HTMLResponse(content=html_content, status_code=200)