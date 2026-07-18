import { useNavigate } from "react-router-dom";
import DifficultyCard from "../components/DifficultyCard";
import difficulties from "../data/difficulties";
import { startSession } from "../services/chatService";

function DifficultySelect(){

    const navigate=useNavigate();

    async function chooseDifficulty(level){

        localStorage.setItem(
            "difficulty",
            JSON.stringify(level)
        );

        const persona=JSON.parse(localStorage.getItem("persona"));

        const scenario=JSON.parse(localStorage.getItem("scenario"));

        const session=await startSession({

            persona:persona.id,

            scenario:scenario.id,

            difficulty:level.id

        });

        localStorage.setItem(
            "sessionId",
            session.sessionId
        );

        navigate("/chat");

    }

    return(

        <div className="min-h-screen bg-slate-900 p-10">

            <h1 className="text-white text-4xl text-center font-bold mb-10">

                Select Difficulty

            </h1>

            <div className="grid md:grid-cols-3 gap-8">

                {

                    difficulties.map(d=>(

                        <DifficultyCard

                            key={d.id}

                            difficulty={d}

                            onSelect={chooseDifficulty}

                        />

                    ))

                }

            </div>

        </div>

    );

}

export default DifficultySelect;