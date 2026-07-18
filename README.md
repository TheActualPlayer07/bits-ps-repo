# AI Job Discovery Agent

![Job Discovery Agent](https://img.shields.io/badge/Status-Complete-success) ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

The **AI Job Discovery Agent** is an intelligent, automated pipeline designed to match candidates with their ideal remote jobs. By leveraging web scraping, relevance scoring algorithms, and OpenAI-powered insights, this agent transforms a simple list of skills into a highly curated, deeply analyzed dashboard of job opportunities.

---

## 🚀 Core Features

1. **Live Web Scraping Engine (`src/scraper.py`)**
   - Automatically fetches real, live programming job postings from We Work Remotely.
   - Extracts essential metadata including Job Title, Company, Location, and Application Links.

2. **Relevance Scoring (`src/scoring.py`)**
   - Intelligently parses user skills and calculates a **Relevance Score (0-100)** for each scraped job.
   - Exact skill matches and title matches are weighted heavier than general descriptions.
   - Filters out irrelevant roles and guarantees the best matches are sorted to the top.

3. **AI Job Insights (`src/ai_insights.py`)**
   - Integrates with the OpenAI API (`gpt-3.5-turbo`) to generate deep, personalized insights for each matched job.
   - Evaluates **Role Fit**, identifies **Skills to Gain**, assesses **Work Culture**, and projects a potential **Career Path**.

4. **Interactive Dashboard (`app.py`)**
   - A clean, modern Streamlit interface.
   - Features structured metric layouts, formatted markdown tags for required skills, and color-coded alert boxes for AI insights.

---

## ⚙️ Tech Stack

- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **Data Manipulation:** Pandas
- **Web Scraping:** Requests, BeautifulSoup4
- **AI / LLM:** OpenAI API
- **Environment Management:** python-dotenv

---

## 🛠️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd Job-Discovery-Agent
   ```

2. **Install dependencies**
   Ensure you have Python 3.8+ installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory (optional, you can also paste your API key directly in the UI):
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

---

## 📖 Usage

1. Launch the app and open your browser to `http://localhost:8501`.
2. Input your skills directly into the text area (e.g., "Python, Machine Learning, Data Science").
3. (Optional) Paste your OpenAI API key in the sidebar to unlock AI Insights.
4. Click **"Discover Jobs"**.
5. The agent will scrape live jobs, score them against your skills, generate AI insights, and present you with a beautifully formatted dashboard!

---

*This project was built over 6 phases, evolving from a mock-data pipeline into a fully automated, AI-driven job scraping engine.*
