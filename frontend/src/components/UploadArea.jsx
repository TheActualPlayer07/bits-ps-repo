import { useState, useRef } from 'react'

const ACCEPTED_EXTENSIONS = ['.pdf', '.docx']
const MAX_FILE_SIZE_MB = 5

function validateFile(file) {
  const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()

  if (!ACCEPTED_EXTENSIONS.includes(extension)) {
    return `Unsupported file type "${extension}". Please upload a PDF or DOCX file.`
  }

  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    return `File is too large. Max size is ${MAX_FILE_SIZE_MB}MB.`
  }

  return null
}

export default function UploadArea({ onFileSelected }) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  function handleFiles(fileList) {
    const file = fileList[0]
    if (!file) return

    const error = validateFile(file)
    onFileSelected(file, error)
  }

  function handleDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  function handleDragOver(e) {
    e.preventDefault()
    setIsDragging(true)
  }

  function handleDragLeave() {
    setIsDragging(false)
  }

  function handleBrowseClick() {
    inputRef.current?.click()
  }

  function handleInputChange(e) {
    handleFiles(e.target.files)
    e.target.value = ''
  }

  return (
    <section
      className={`upload-area ${isDragging ? 'upload-area--dragging' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={handleBrowseClick}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        onChange={handleInputChange}
        hidden
      />
      <svg className="upload-area__icon" width="48" height="48" viewBox="0 0 24 24" fill="none">
        <path d="M7 18a4 4 0 01-.9-7.9A5 5 0 0116 7a4.5 4.5 0 011 8.9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M12 12v7m0-7l-2.5 2.5M12 12l2.5 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      <p className="upload-area__text">Drop your resume here</p>
      <p className="upload-area__subtext">or <span className="upload-area__link">click to browse</span></p>
      <p className="upload-area__hint">PDF or DOCX, up to {MAX_FILE_SIZE_MB}MB</p>
    </section>
  )
}