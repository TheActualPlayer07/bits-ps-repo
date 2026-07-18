import { useLocation, useNavigate } from "react-router-dom";

function Debrief() {

  const navigate = useNavigate();

  const { state } = useLocation();

  if (!state) {

    return (

      <div className="min-h-screen flex justify-center items-center bg-slate-900 text-white">

        No Debrief

      </div>

    );

  }

  const feedback = state.feedback;

  return (

    <div className="min-h-screen bg-slate-900 text-white p-10">

      <h1 className="text-5xl font-bold mb-8">

        Conversation Debrief

      </h1>

      <div className="grid grid-cols-4 gap-5 mb-10">

        <div className="bg-slate-800 p-5 rounded-xl">

          <p>Overall</p>

          <h2 className="text-4xl font-bold">

            {feedback.overall}/10

          </h2>

        </div>

        <div className="bg-slate-800 p-5 rounded-xl">

          <p>Discovery</p>

          <h2 className="text-4xl font-bold">

            {feedback.discovery}/10

          </h2>

        </div>

        <div className="bg-slate-800 p-5 rounded-xl">

          <p>Communication</p>

          <h2 className="text-4xl font-bold">

            {feedback.communication}/10

          </h2>

        </div>

        <div className="bg-slate-800 p-5 rounded-xl">

          <p>Objections</p>

          <h2 className="text-4xl font-bold">

            {feedback.objectionHandling}/10

          </h2>

        </div>

      </div>

      <div className="grid grid-cols-2 gap-8">

        <div className="bg-slate-800 rounded-xl p-6">

          <h2 className="text-2xl font-bold mb-4">

            Strengths

          </h2>

          <ul className="list-disc ml-6">

            {

              feedback.strengths.map((item, i) => (

                <li key={i} className="mb-2">

                  {item}

                </li>

              ))

            }

          </ul>

        </div>

        <div className="bg-slate-800 rounded-xl p-6">

          <h2 className="text-2xl font-bold mb-4">

            Weaknesses

          </h2>

          <ul className="list-disc ml-6">

            {

              feedback.weaknesses.map((item, i) => (

                <li key={i} className="mb-2">

                  {item}

                </li>

              ))

            }

          </ul>

        </div>

      </div>

      <div className="bg-slate-800 rounded-xl p-6 mt-8">

        <h2 className="text-2xl font-bold mb-3">

          Next Time

        </h2>

        <p>

          {feedback.nextTime}

        </p>

      </div>

      <button

        onClick={() => navigate("/")}

        className="mt-8 bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-xl"

      >

        Start New Session

      </button>

    </div>

  );

}

export default Debrief;