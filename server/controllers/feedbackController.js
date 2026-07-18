import { generateFeedback } from "../services/feedbackService.js";

export async function getFeedback(req, res) {

  try {

    const { transcript, stats } = req.body;

    const feedback = await generateFeedback(
      transcript,
      stats
    );

    res.json(feedback);

  } catch (err) {

    console.error(err);

    res.status(500).json({
      error: err.message
    });

  }

}