const TITLE_TEXT = 'Turn your resume into structured insights'
const SUBTITLE_TEXT = 'Upload your unstructured resume to convert it to valuable insights like capabilities, business services, value constructs, achievement cards and get recommendations for improvements'

function scatterChars(text, className, seedOffset) {
  return text.split('').map((char, index) => {
    if (char === ' ') return null
    const seed = index + seedOffset
    return (
      <span
        key={seed}
        className={className}
        style={{
          top: `${(seed * 17) % 92}%`,
          left: `${(seed * 41) % 90}%`,
          transform: `rotate(${((seed * 23) % 70) - 35}deg)`,
        }}
      >
        {char}
      </span>
    )
  })
}

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero__left">
        <h1 className="hero__title">{TITLE_TEXT}</h1>
        <p className="hero__subtitle">{SUBTITLE_TEXT}</p>
      </div>

      <div className="hero__divider"></div>

      <div className="hero__right">
        {scatterChars(TITLE_TEXT, 'hero__scatter-char hero__scatter-char--title', 0)}
        {scatterChars(SUBTITLE_TEXT, 'hero__scatter-char hero__scatter-char--subtitle', 100)}
      </div>
    </section>
  )
}