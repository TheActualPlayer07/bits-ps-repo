import { useState } from 'react'

export default function GetInsightButton({ selectedFile, onParseComplete }) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleClick() {
    console.log('Button clicked')
    if (!selectedFile) return

    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('resume', selectedFile)

      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/resume/parse`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Something went wrong while parsing.')
      }

      const data = await response.json()

      // Expecting shape: { valueConstructs: {...}, achievements: [...], suggestions: [...] }
      onParseComplete(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      <button className="parse-button" onClick={handleClick} disabled={isLoading}>
        <svg className="parse-button__icon" viewBox="0 0 24 24" fill="none">
          <path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        {isLoading ? 'Analyzing...' : 'Generate Insights'}
      </button>
      {error && <p className="parse-button__error">{error}</p>}
    </>
  )
}