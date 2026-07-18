import api from "./api";

export async function startSession(data) {
  const res = await api.post("/roleplay/start-session", data);
  return res.data;
}

export async function sendMessage(data) {
  const res = await api.post("/roleplay/chat", data);
  return res.data;
}

export async function endSession(sessionId) {
  const res = await api.post("/roleplay/end-session", {
    sessionId,
  });

  return res.data;
}

export async function getFeedback(data) {
  const res = await api.post("/feedback", data);

  return res.data;
}