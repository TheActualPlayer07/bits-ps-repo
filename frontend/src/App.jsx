import { useState, useRef, useEffect } from 'react'
import Navbar from './components/NavBar.jsx'
import Hero from './components/Hero.jsx'
import UploadArea from './components/UploadArea.jsx'
import StatusBanner from './components/StatusBanner.jsx'
import GetInsightButton from './components/GetInsightButton.jsx'
import ResultsSection from './components/ResultsSection.jsx'
import AboutSection from './components/About.jsx'
import Footer from './components/Footer.jsx'
import './App.css'

export default function App() {
  const [status, setStatus] = useState(null)
  const [message, setMessage] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [parsedResult, setParsedResult] = useState(null)
  const resultsRef = useRef(null)

  function handleFileSelected(file, error) {
    if (error) {
      setStatus('error')
      setMessage(error)
      setSelectedFile(null)
      setParsedResult(null)
      return
    }

    setStatus('success')
    setMessage(`"${file.name}" ready to upload.`)
    setSelectedFile(file)
    setParsedResult(null)
  }

  function handleParseComplete(data) {
    setParsedResult(data)
  }

  useEffect(() => {
    if (parsedResult && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [parsedResult])

  return (
    <>
      <Navbar />
      <Hero />
      <div className="upload-section">
        <UploadArea onFileSelected={handleFileSelected} />
        <StatusBanner status={status} message={message} />
        {status === 'success' && (
          <GetInsightButton
            selectedFile={selectedFile}
            onParseComplete={handleParseComplete}
          />
        )}
      </div>

      {parsedResult && (
        <div ref={resultsRef}>
          <ResultsSection result={parsedResult} />
        </div>
      )}

      <AboutSection />
      <Footer />
    </>
  )
}