const sessions = {};

export function createSession(id, data) {
  sessions[id] = {
    ...data,

    history: [],

    trust: 40,

    interest: 50,

    objectionsRaised: 0,

    discoveryQuestions: 0,

    phase: "opening",

    summary: ""
  };
}

export function getSession(id) {
  return sessions[id];
}

export function deleteSession(id) {
  delete sessions[id];
}

export function updateHistory(id, role, message) {

  sessions[id].history.push({

    role,

    message

  });

}

export function updateConversation(id, userMessage) {

  const session = sessions[id];

  const lower = userMessage.toLowerCase();

  if (
    lower.includes("why") ||
    lower.includes("how") ||
    lower.includes("what") ||
    lower.includes("?")
  ) {

    session.discoveryQuestions++;

    session.trust += 3;

  }

  if (
    lower.includes("buy") ||
    lower.includes("purchase") ||
    lower.includes("our product")
  ) {

    session.interest -= 4;

  }

  if (session.discoveryQuestions > 3)
    session.phase = "discovery";

  if (session.discoveryQuestions > 6)
    session.phase = "needs";

  if (session.discoveryQuestions > 9)
    session.phase = "solution";

  session.trust = Math.max(0, Math.min(100, session.trust));

  session.interest = Math.max(0, Math.min(100, session.interest));

}

export function getPromptStats(id){

    const s=sessions[id];

    return{

        trust:s.trust,

        interest:s.interest,

        objections:s.objectionsRaised,

        questions:s.discoveryQuestions,

        phase:s.phase

    };

}