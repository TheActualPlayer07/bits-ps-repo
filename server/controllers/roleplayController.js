import { v4 as uuid } from "uuid";

import {
  createSession,
  getSession,
  updateHistory,
  deleteSession,
  updateConversation,
  getPromptStats
} from "../services/conversationService.js";

import { buildPrompt } from "../services/promptService.js";
import { generateResponse } from "../services/geminiService.js";

export function startSession(req,res){

const {persona,scenario,difficulty}=req.body;

if(!persona||!scenario||!difficulty){

return res.status(400).json({

error:"Missing fields"

});

}

const id=uuid();

createSession(id,{

persona,

scenario,

difficulty

});

res.json({

sessionId:id

});

}

export async function chat(req,res){

try{

const {sessionId,message}=req.body;

const session=getSession(sessionId);

if(!session){

return res.status(404).json({

error:"Session not found"

});

}

updateConversation(

sessionId,

message

);

updateHistory(

sessionId,

"Student",

message

);

const history=session.history

.map(

m=>`${m.role}: ${m.message}`

)

.join("\n");

const stats=getPromptStats(sessionId);

const prompt=buildPrompt(

session.persona,

session.scenario,

session.difficulty,

history,

stats

);

const reply=await generateResponse(prompt);

updateHistory(

sessionId,

"Persona",

reply

);

res.json({

reply,

stats

});

}

catch(err){

console.log(err);

res.status(500).json({

error:err.message

});

}

}

export function endSession(req,res){

const {sessionId}=req.body;

const session=getSession(sessionId);

if(!session){

return res.status(404).json({

error:"Session not found"

});

}

const transcript=session.history;

const stats=getPromptStats(sessionId);

deleteSession(sessionId);

res.json({

transcript,

stats

});

}