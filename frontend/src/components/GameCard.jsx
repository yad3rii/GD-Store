import { Link } from "react-router-dom";
import Price from "./Price";
export default function GameCard({ game }) {
  return (
    <Link to={`/game/${game.slug}`} className="game-card">
      <div className="card-image">
        {game.cover_image ? (
          <img src={game.cover_image} alt="" loading="lazy" />
        ) : (
          <div className="image-fallback">GD STORE</div>
        )}
        <span className="card-overlay">Подробнее ↗</span>
      </div>
      <div className="card-body">
        <p className="game-genre">
          {game.genres?.map((g) => g.name).join(" · ") || "Игра для ПК"}
        </p>
        <h3>{game.title}</h3>
        <Price game={game} />
      </div>
    </Link>
  );
}
