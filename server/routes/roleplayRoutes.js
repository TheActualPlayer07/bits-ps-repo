import express from "express";

import {
  startSession,
  chat,
  endSession,
} from "../controllers/roleplayController.js";

const router = express.Router();

router.post("/start-session", startSession);

router.post("/chat", chat);

router.post("/end-session", endSession);

export default router;