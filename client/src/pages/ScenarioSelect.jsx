import { useNavigate } from "react-router-dom";
import ScenarioCard from "../components/ScenarioCard";
import scenarios from "../data/scenarios";

function ScenarioSelect() {

  const navigate = useNavigate();

  function chooseScenario(scenario){

    localStorage.setItem(
      "scenario",
      JSON.stringify(scenario)
    );

    navigate("/difficulty");

  }

  return(

    <div className="min-h-screen bg-slate-900 p-10">

      <h1 className="text-white text-4xl text-center font-bold mb-10">

        Choose Scenario

      </h1>

      <div className="grid md:grid-cols-2 gap-8">

        {
          scenarios.map(s=>(
            <ScenarioCard
              key={s.id}
              scenario={s}
              onSelect={chooseScenario}
            />
          ))
        }

      </div>

    </div>

  );

}

export default ScenarioSelect;