import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import roleplayRoutes from "./routes/roleplayRoutes.js";
import feedbackRoutes from "./routes/feedbackRoutes.js";

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("Sales Roleplay Agent API Running");
});

app.use("/api/roleplay", roleplayRoutes);
app.use("/api/feedback", feedbackRoutes);

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});