import { useNavigate } from "react-router-dom";

function Home() {

    const navigate = useNavigate();

    return (

        <div className="min-h-screen flex flex-col justify-center items-center bg-slate-900 text-white">

            <h1 className="text-5xl font-bold mb-6">
                AI Sales Roleplay Agent
            </h1>

            <p className="text-xl mb-10 text-gray-300">

                Practice Business Development Conversations
                with AI Personas

            </p>

            <button

                onClick={() => navigate("/persona")}

                className="bg-blue-600 px-8 py-4 rounded-lg text-lg hover:bg-blue-700"

            >

                Start Practicing

            </button>

        </div>

    );

}

export default Home;