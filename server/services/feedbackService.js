import { generateResponse } from "./geminiService.js";

export async function generateFeedback(transcript, stats) {
  const conversation = transcript
    .map((m) => `${m.role}: ${m.message}`)
    .join("\n");

  const prompt = `
You are an expert Business Development trainer.

Analyze the following conversation.

${conversation}

Conversation Metrics

Trust: ${stats.trust}
Interest: ${stats.interest}
Discovery Questions: ${stats.questions}
Conversation Phase: ${stats.phase}

Return ONLY valid JSON.

{
  "overall": number,
  "discovery": number,
  "communication": number,
  "objectionHandling": number,
  "strengths":[
      "...",
      "...",
      "..."
  ],
  "weaknesses":[
      "...",
      "...",
      "..."
  ],
  "nextTime":"..."
}

Scores must be between 1 and 10.

Do not wrap in markdown.
Do not explain anything.
`;

  const response = await generateResponse(prompt);

  try {
    return JSON.parse(response);
  } catch {
    return {
      overall: 6,
      discovery: 6,
      communication: 6,
      objectionHandling: 6,
      strengths: ["Good effort."],
      weaknesses: ["Could not parse AI feedback."],
      nextTime: "Try again."
    };
  }
}