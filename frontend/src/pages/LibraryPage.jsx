import { useState } from "react";
import { useAuthStore } from "../store/authStore";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getLibrary } from "../api/store";
import GameCard from "../components/GameCard";
import Icon from "../components/Icon";
export default function LibraryPage() {
  const [page, setPage] = useState(1);
  const {accessToken, sessionId} = useAuthStore();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["library", sessionId, page],
    queryFn: ({signal}) => getLibrary(page, {signal}),
    enabled: Boolean(accessToken),
  });
  if (!accessToken) return <div className="empty-state"><Link to="/login">Войдите, чтобы открыть библиотеку</Link></div>;
  return (
    <section className="catalog-page">
      <p className="eyebrow">Ваши миры всегда рядом</p>
      <h1>Библиотека</h1>
      {isLoading ? (
        <div className="empty-state" role="status">
          Загружаем коллекцию…
        </div>
      ) : error ? (
        <div className="empty-state" role="alert">
          <h2>Не удалось загрузить библиотеку</h2>
          <Link to="/login">Войти в аккаунт</Link>
          <button onClick={() => refetch()}>Повторить</button>
        </div>
      ) : data?.results?.length ? (
        <div className="game-grid" style={{ marginTop: 30 }}>
          {data.results.map((e) => (
            <GameCard key={e.id} game={e.game} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <Icon name="library" size={44} />
          <h2>Ваша коллекция ещё впереди</h2>
          <p>Здесь появятся приобретённые игры.</p>
          <Link className="button primary" to="/">
            Открыть магазин
          </Link>
        </div>
      )}
      {(data?.next || data?.previous) && <div className="pagination">
        <button disabled={!data.previous || isLoading} onClick={() => setPage(p => p - 1)}>Назад</button>
        <span>Страница {page}</span>
        <button disabled={!data.next || isLoading} onClick={() => setPage(p => p + 1)}>Далее</button>
      </div>}
    </section>
  );
}
