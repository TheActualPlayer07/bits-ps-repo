function DifficultyCard({ difficulty, onSelect }) {
  return (
    <div
      onClick={() => onSelect(difficulty)}
      className="bg-slate-800 p-6 rounded-xl cursor-pointer hover:bg-slate-700"
    >
      <h2 className="text-white text-xl font-bold">
        {difficulty.name}
      </h2>

      <p className="text-gray-400 mt-3">
        {difficulty.description}
      </p>
    </div>
  );
}

export default DifficultyCard;