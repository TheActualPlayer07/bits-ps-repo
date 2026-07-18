export default function AboutSection() {
  return (
    <section className="about-section">
      <h2 className="about-section__title">How it works</h2>
      <div className="about-section__steps">
        <div className="about-step">
          <svg className="about-step__icon" width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h3>Upload</h3>
          <p>Upload your resume as a PDF or DOCX file. You should see a ready to upload message if upload is successful and an error otherwise. Click on the Generate Insights button to get results.</p>
        </div>
        <div className="about-step">
          <svg className="about-step__icon" width="28" height="28" viewBox="0 0 24 24" fill="none">
            <circle cx="10" cy="10" r="6" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M15 15l5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <h3>Extraction</h3>
          <p>We go through your resume and analyze it for insights like capabilities, business services, and value constructs which are derived from your work experience, projects etc..</p>
        </div>
        <div className="about-step">
          <svg className="about-step__icon" width="28" height="28" viewBox="0 0 24 24" fill="none">
            <rect x="4" y="4" width="16" height="16" rx="3" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M8 12l2.5 2.5L16 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h3>Structured Output</h3>
          <p>Get clean, organized and structured output consisting of insights on your present state and key recommendations on what needs improvement.</p>
        </div>
      </div>
    </section>
  )
}