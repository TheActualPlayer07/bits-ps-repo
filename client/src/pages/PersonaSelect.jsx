import { useNavigate } from "react-router-dom";
import PersonaCard from "../components/PersonaCard";
import personas from "../data/personas";

function PersonaSelect() {

  const navigate = useNavigate();

  function handleSelect(persona){

    localStorage.setItem(
      "persona",
      JSON.stringify(persona)
    );

    navigate("/scenario");

  }

  return (

    <div className="min-h-screen bg-slate-900 p-10">

      <h1 className="text-4xl font-bold text-white text-center mb-10">

        Choose a Persona

      </h1>

      <div className="grid md:grid-cols-3 gap-8">

        {

          personas.map(persona=>(

            <PersonaCard

              key={persona.id}

              persona={persona}

              onSelect={handleSelect}

            />

          ))

        }

      </div>

    </div>

  );

}

export default PersonaSelect;