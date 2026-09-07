import { Link, useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getGame } from "../api/catalog";
import { addToCart } from "../api/store";
import Price from "../components/Price";
import Icon from "../components/Icon";
export default function GamePage() {
  const { slug } = useParams(),
    qc = useQueryClient();
  const {
    data: game,
    isLoading,
    error,
    refetch,
  } = useQuery({ queryKey: ["game", slug], queryFn: () => getGame(slug) });
  const add = useMutation({
    mutationKey: ["add", slug],
    mutationFn: () => addToCart(game.id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["cart"] }),
  });
  if (isLoading)
    return (
      <div className="empty-state" role="status">
        Загружаем игру…
      </div>
    );
  if (error || !game)
    return (
      <div className="empty-state" role="alert">
        <h1>Не удалось открыть игру</h1>
        <button className="button" onClick={() => refetch()}>
          Повторить
        </button>
        <Link to="/">Вернуться в магазин</Link>
      </div>
    );
  return (
    <>
      <div className="detail-heading">
        <Link className="breadcrumb" to="/">
          Магазин /{" "}
        </Link>
        <h1>{game.title}</h1>
      </div>
      <div className="detail-grid">
        <img
          className="detail-image"
          src={game.screenshots?.[0]?.image || game.cover_image}
          alt={game.title}
        />
        <aside className="detail-panel">
          <div className="hero-genres">
            {game.genres?.map((g) => (
              <span key={g.id}>{g.name}</span>
            ))}
          </div>
          <h2>{game.title}</h2>
          <p>{game.short_description}</p>
          <Price game={game} />
          <button
            className="button primary"
            disabled={add.isPending}
            onClick={() => add.mutate()}
          >
            <Icon name="cart" />
            {add.isPending ? "Добавляем…" : "Добавить в корзину"}
          </button>
          {add.isSuccess && (
            <Link className="status-message" to="/cart" role="status">
              Игра в корзине. Перейти →
            </Link>
          )}
          {add.isError && (
            <p className="error-message" role="alert">
              Не удалось добавить игру. Проверьте, выполнен ли вход, и
              попробуйте снова.
            </p>
          )}
        </aside>
      </div>
      <section className="detail-description">
        <h2>Об игре</h2>
        <p>{game.description}</p>
      </section>
    </>
  );
}
