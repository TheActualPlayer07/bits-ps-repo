import { useState } from 'react'

function CopyButton({ textToCopy }) {
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    navigator.clipboard.writeText(textToCopy)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <button className="copy-button" onClick={handleCopy}>
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

function ValueConstructsCard({ data }) {
  const text = [
    'Business Services:', ...(data.businessServices || []),
    '', 'Capabilities:', ...(data.capabilities || []),
    '', 'Skills:', ...(data.skills || []),
  ].join('\n')

  return (
    <div className="result-card result-card--constructs">
      <div className="result-card__header">
        <h3>Value Constructs</h3>
        <CopyButton textToCopy={text} />
      </div>

      <div className="result-card__group">
        <h4>Business Services</h4>
        <div className="result-card__tags">
          {data.businessServices?.length ? (
            data.businessServices.map((item, i) => <span key={i} className="tag">{item}</span>)
          ) : (
            <p className="result-card__empty">None found</p>
          )}
        </div>
      </div>

      <div className="result-card__group">
        <h4>Capabilities</h4>
        <div className="result-card__tags">
          {data.capabilities?.length ? (
            data.capabilities.map((item, i) => <span key={i} className="tag">{item}</span>)
          ) : (
            <p className="result-card__empty">None found</p>
          )}
        </div>
      </div>

      <div className="result-card__group">
        <h4>Skills</h4>
        <div className="result-card__tags">
          {data.skills?.length ? (
            data.skills.map((item, i) => <span key={i} className="tag">{item}</span>)
          ) : (
            <p className="result-card__empty">None found</p>
          )}
        </div>
      </div>
    </div>
  )
}

function AchievementsCard({ data }) {
  const text = data.map((item) => `${item.title}: ${item.description}`).join('\n\n')

  return (
    <div className="result-card result-card--achievements">
      <div className="result-card__header">
        <h3>Achievements</h3>
        <CopyButton textToCopy={text} />
      </div>

      {data.length ? (
        data.map((item, i) => (
          <div key={i} className="achievement-item">
            <h4>{item.title}</h4>
            <p>{item.description}</p>
          </div>
        ))
      ) : (
        <p className="result-card__empty">No achievements found</p>
      )}
    </div>
  )
}

function SuggestionsCard({ data }) {
  const text = data.map((item, i) => `${i + 1}. ${item}`).join('\n')

  return (
    <div className="result-card result-card--suggestions">
      <div className="result-card__header">
        <h3>Suggestions</h3>
        <CopyButton textToCopy={text} />
      </div>

      {data.length ? (
        <ul className="result-card__list">
          {data.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="result-card__empty">No suggestions</p>
      )}
    </div>
  )
}

export default function ResultsSection({ result }) {
  if (!result) return null

  return (
    <section className="results-section">
      <h2 className="results-section__title">Your Insights</h2>
      <div className="results-section__grid">
        <ValueConstructsCard data={result.valueConstructs} />
        <AchievementsCard data={result.achievements} />
        <SuggestionsCard data={result.suggestions} />
      </div>
    </section>
  )
}