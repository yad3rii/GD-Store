import { Link } from "react-router-dom";

export default function GameCard({ game }) {
  return (
    <Link
      to={`/game/${game.slug}`}
      className="block bg-slate-800 rounded-lg overflow-hidden hover:scale-[1.02] transition"
    >
      {game.cover_image && (
        <img src={game.cover_image} alt={game.title} className="w-full h-40 object-cover" />
      )}
      <div className="p-3">
        <h3 className="font-semibold truncate">{game.title}</h3>
        <div className="flex items-center gap-2 mt-1">
          {game.discount_percent > 0 && (
            <span className="text-green-400 text-xs bg-green-900 px-1.5 py-0.5 rounded">
              -{game.discount_percent}%
            </span>
          )}
          <span className="text-sm">{game.final_price} ₴</span>
        </div>
      </div>
    </Link>
  );
}
