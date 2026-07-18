function ScenarioCard({ scenario, onSelect }) {
  return (
    <div
      onClick={() => onSelect(scenario)}
      className="bg-slate-800 p-6 rounded-xl cursor-pointer hover:bg-slate-700 transition shadow-lg"
    >
      <h2 className="text-white text-xl font-bold">
        {scenario.name}
      </h2>

      <p className="text-gray-400 mt-3">
        {scenario.description}
      </p>
    </div>
  );
}

export default ScenarioCard;