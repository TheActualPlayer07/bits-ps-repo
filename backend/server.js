require('dotenv').config()
const express = require('express')
const cors = require('cors')
const multer = require('multer')
const { PDFParse } = require('pdf-parse')
const mammoth = require('mammoth')
const Groq = require('groq-sdk')

const app = express()
const PORT = process.env.PORT || 3000

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY })

app.use(cors())

const upload = multer({ storage: multer.memoryStorage() })

app.get('/', (req, res) => {
  res.send('Backend is running')
})

async function extractText(file) {
  const extension = file.originalname.slice(file.originalname.lastIndexOf('.')).toLowerCase()

  if (extension === '.pdf') {
    const parser = new PDFParse({ data: file.buffer })
    const result = await parser.getText()
    await parser.destroy()
    return result.text
  }

  if (extension === '.docx') {
    const result = await mammoth.extractRawText({ buffer: file.buffer })
    return result.value
  }

  throw new Error('Unsupported file type')
}

const SYSTEM_PROMPT = `You are a resume analysis engine. Given raw resume text, extract three things and respond with ONLY valid JSON (no extra text before or after) matching exactly this structure:

{
  "valueConstructs": {
    "businessServices": ["string", "..."],
    "capabilities": ["string", "..."],
    "skills": ["string", "..."]
  },
  "achievements": [
    { "title": "string", "description": "string" }
  ],
  "suggestions": [
    "string"
  ]
}

Rules:
- businessServices: high-level services this person could deliver to a company (e.g. "Backend API Development", "Data Pipeline Engineering")
- capabilities: broader professional capabilities demonstrated (e.g. "Cross-functional Collaboration", "System Design")
- skills: specific technical or tool-based skills (e.g. "Python", "React", "AWS EC2")
- achievements: distinct, resume-worthy accomplishments with a short title and one-sentence description
- suggestions: concrete, actionable improvements for the resume (missing quantification, unclear phrasing, formatting issues, etc.)
- If a category has no clear content, return an empty array for it — do not invent information not present in the resume.
- Respond with ONLY the JSON object. No markdown code fences, no explanation.`

async function getInsightsFromGroq(resumeText) {
  const completion = await groq.chat.completions.create({
    model: 'openai/gpt-oss-120b',
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: resumeText },
    ],
    temperature: 0.3,
  })

  const rawResponse = completion.choices[0].message.content

  // Defensive cleanup: strip anything before the first { and after the last }
  const jsonStart = rawResponse.indexOf('{')
  const jsonEnd = rawResponse.lastIndexOf('}')
  const jsonString = rawResponse.slice(jsonStart, jsonEnd + 1)

  return JSON.parse(jsonString)
}

app.post('/api/resume/parse', upload.single('resume'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' })
  }

  try {
    const extractedText = await extractText(req.file)
    const insights = await getInsightsFromGroq(extractedText)

    res.json(insights)
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Failed to generate insights' })
  }
})

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})