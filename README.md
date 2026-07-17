
# Strategic AI Outreach Agent 📨⚡

An enterprise-grade AI agent that transforms structured company research into highly personalized, vendor-agnostic executive outreach. 

Unlike standard "AI email generators" that rely on marketing fluff, this agent operates like an independent Systems Architect. It diagnoses systemic bottlenecks, architects a technical resolution, and drafts peer-to-peer outreach designed to start genuine conversations with technical executives.

## 🧠 System Architecture

The pipeline is strictly modular, ensuring zero hallucinations and perfect traceability:
1. **Ingestion Engine (`ingestion.py`):** Parses and validates structured research profiles using Pydantic.
2. **Inference Engine (`inference.py`):** Diagnoses hidden operational problems and root causes based purely on the evidence provided.
3. **Strategic Mapping (`mapping.py`):** Acts as an independent consultant, evaluating multiple service categories and selecting the highest-impact architectural intervention.
4. **Copywriting Engine (`drafting.py`):** Translates the strategy into three highly natural, human-grade email variants across a continuous tone spectrum.
5. **Console UI (`app.py`):** A clean, Streamlit-based executive dashboard to orchestrate the pipeline.

## 🚀 Live Demo
[Insert your Streamlit app link here once deployed]

## 🛠️ Tech Stack
- **Language:** Python
- **LLM Orchestration:** Groq API (`qwen/qwen3-32b` / `llama-3.3-70b-versatile`)
- **Data Validation:** Pydantic
- **User Interface:** Streamlit

## 💻 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
