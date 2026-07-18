function PersonaCard({ persona, onSelect }) {
  return (
    <div
      onClick={() => onSelect(persona)}
      className="bg-slate-800 rounded-xl p-6 cursor-pointer hover:bg-slate-700 transition shadow-lg"
    >
      <div className="text-5xl mb-4">{persona.emoji}</div>

      <h2 className="text-xl font-bold text-white">
        {persona.name}
      </h2>

      <p className="text-gray-400 mt-3">
        {persona.description}
      </p>
    </div>
  );
}

export default PersonaCard;