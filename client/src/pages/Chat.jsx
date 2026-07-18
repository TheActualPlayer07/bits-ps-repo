import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  sendMessage,
  endSession,
  getFeedback,
} from "../services/chatService";

function Chat() {

  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);

  const [stats, setStats] = useState(null);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  async function handleSend() {

    if (!input.trim()) return;

    const userMessage = input;

    setMessages(prev => [

      ...prev,

      {

        role: "You",

        text: userMessage

      }

    ]);

    setInput("");

    setLoading(true);

    try {

      const sessionId = localStorage.getItem("sessionId");

      const res = await sendMessage({

        sessionId,

        message: userMessage

      });

      setStats(res.stats);

      setMessages(prev => [

        ...prev,

        {

          role: "AI",

          text: res.reply

        }

      ]);

    }

    catch (err) {

      console.error(err);

    }

    setLoading(false);

  }

  async function finishConversation() {

    const sessionId = localStorage.getItem("sessionId");

    const session = await endSession(sessionId);

    const feedback = await getFeedback({

      transcript: session.transcript,

      stats: session.stats

    });

    navigate("/debrief", {

      state: {

        feedback: feedback

      }

    });

  }

  return (

    <div className="min-h-screen bg-slate-900 text-white p-8">

      <div className="flex justify-between items-center">

        <h1 className="text-4xl font-bold">

          Sales Roleplay

        </h1>

        <button

          onClick={finishConversation}

          className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-lg"

        >

          End Session

        </button>

      </div>

      {

        stats &&

        <div className="grid grid-cols-4 gap-4 my-6">

          <div className="bg-slate-800 rounded-lg p-4">

            <p className="text-gray-400">Trust</p>

            <h2 className="text-2xl font-bold">

              {stats.trust}

            </h2>

          </div>

          <div className="bg-slate-800 rounded-lg p-4">

            <p className="text-gray-400">Interest</p>

            <h2 className="text-2xl font-bold">

              {stats.interest}

            </h2>

          </div>

          <div className="bg-slate-800 rounded-lg p-4">

            <p className="text-gray-400">Phase</p>

            <h2 className="text-xl font-bold">

              {stats.phase}

            </h2>

          </div>

          <div className="bg-slate-800 rounded-lg p-4">

            <p className="text-gray-400">Questions</p>

            <h2 className="text-2xl font-bold">

              {stats.questions}

            </h2>

          </div>

        </div>

      }

      <div className="bg-slate-800 rounded-xl h-[500px] overflow-y-auto p-6">

        {

          messages.length === 0 &&

          <p className="text-center text-gray-500 mt-40">

            Start chatting...

          </p>

        }

        {

          messages.map((m, i) => (

            <div

              key={i}

              className={`mb-5 flex ${m.role === "You" ? "justify-end" : "justify-start"}`}

            >

              <div

                className={`max-w-[70%] rounded-xl p-4 ${m.role === "You"

                    ? "bg-blue-600"

                    : "bg-slate-700"

                  }`}

              >

                <p className="font-bold mb-2">

                  {m.role}

                </p>

                <p>

                  {m.text}

                </p>

              </div>

            </div>

          ))

        }

      </div>

      <div className="flex gap-3 mt-6">

        <input

          value={input}

          onChange={(e) => setInput(e.target.value)}

          onKeyDown={(e) => {

            if (e.key === "Enter")

              handleSend();

          }}

          className="flex-1 p-4 rounded-lg bg-white text-black"

          placeholder="Type your message..."

        />

        <button

          onClick={handleSend}

          disabled={loading}

          className="bg-blue-600 hover:bg-blue-700 px-8 rounded-lg"

        >

          Send

        </button>

      </div>

    </div>

  );

}

export default Chat;