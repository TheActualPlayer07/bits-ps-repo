export function calculateScore(session) {

    let score = 50;

    score += session.discoveryQuestions * 4;

    score += Math.floor(session.trust / 10);

    score += Math.floor(session.interest / 10);

    if (session.phase === "solution")
        score += 10;

    if (score > 100)
        score = 100;

    if (score < 0)
        score = 0;

    return {

        overall: score,

        trust: session.trust,

        interest: session.interest,

        discovery: session.discoveryQuestions,

        phase: session.phase

    };

}