import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getGames, getGenres } from "../api/catalog";
import GameCard from "../components/GameCard";
import Price from "../components/Price";
import Icon from "../components/Icon";
function SectionTitle({ eyebrow, title, link = "/?view=catalog" }) {
  return (
    <div className="section-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2>{title}</h2>
      </div>
      <Link className="text-link" to={link}>
        Смотреть все <Icon name="arrow" size={17} />
      </Link>
    </div>
  );
}
export default function StorePage() {
  const [params, setParams] = useSearchParams();
  const [slide, setSlide] = useState(0);
  const view = params.get("view") || "overview",
    search = params.get("search") || "",
    genre = params.get("genre") || "",
    order = params.get("ordering") || "",
    page = Number(params.get("page") || 1);
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["games", search, genre, order, page],
    queryFn: () => getGames({ search, genres: genre, ordering: order, page }),
  });
  const { data: genreData } = useQuery({
    queryKey: ["genres"],
    queryFn: getGenres,
  });
  const genres = Array.isArray(genreData)
    ? genreData
    : genreData?.results || [];
  const games = data?.results || [],
    featured = games.slice(0, 4),
    game = featured[slide % (featured.length || 1)];
  const setFilter = (key, value) => {
    const next = new URLSearchParams(params);
    value ? next.set(key, value) : next.delete(key);
    next.set("view", "catalog");
    next.delete("page");
    setParams(next);
  };
  if (isLoading)
    return (
      <div role="status">
        <div className="skeleton hero-skeleton" />
        <p>Загружаем игры…</p>
      </div>
    );
  if (error)
    return (
      <div className="empty-state" role="alert">
        <h1>Каталог пока недоступен</h1>
        <p>Не удалось связаться с сервером.</p>
        <button className="button primary" onClick={() => refetch()}>
          Повторить
        </button>
      </div>
    );
  if (view !== "overview" || search || genre) {
    const list =
      view === "sale" ? games.filter((g) => g.discount_percent > 0) : games;
    return (
      <section className="catalog-page">
        <p className="eyebrow">Найдите свою следующую историю</p>
        <h1>{view === "sale" ? "Игры со скидками" : "Каталог игр"}</h1>
        <div className="catalog-filters">
          <label>
            Жанр
            <select
              value={genre}
              onChange={(e) => setFilter("genre", e.target.value)}
            >
              <option value="">Все жанры</option>
              {genres.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Сортировка
            <select
              value={order}
              onChange={(e) => setFilter("ordering", e.target.value)}
            >
              <option value="">Рекомендуемые</option>
              <option value="price">Сначала дешевле</option>
              <option value="-price">Сначала дороже</option>
              <option value="-created_at">Сначала новые</option>
            </select>
          </label>
          {search && <span>Поиск: «{search}»</span>}
          <Link to="/?view=catalog" className="text-link">
            Сбросить фильтры
          </Link>
        </div>
        {list.length ? (
          <div className="game-grid">
            {list.map((g) => (
              <GameCard key={g.id} game={g} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <Icon name="search" size={38} />
            <h2>Ничего не найдено</h2>
            <p>Измените запрос или сбросьте фильтры.</p>
          </div>
        )}
        {(data?.next || data?.previous) && (
          <div className="pagination">
            <button
              disabled={!data.previous}
              onClick={() => {
                const n = new URLSearchParams(params);
                n.set("page", page - 1);
                setParams(n);
              }}
            >
              ← Назад
            </button>
            <span>Страница {page}</span>
            <button
              disabled={!data.next}
              onClick={() => {
                const n = new URLSearchParams(params);
                n.set("page", page + 1);
                setParams(n);
              }}
            >
              Далее →
            </button>
          </div>
        )}
      </section>
    );
  }
  if (!game)
    return (
      <div className="empty-state">
        <h1>Скоро здесь появятся игры</h1>
        <p>Каталог ещё не заполнен.</p>
      </div>
    );
  return (
    <>
      <section className="hero" aria-label="Избранные игры">
        {game.cover_image && (
          <img className="hero-art" src={game.cover_image} alt="" />
        )}
        <div className="hero-shade" />
        <div className="hero-content">
          <span className="hero-badge">
            <i />В центре внимания
          </span>
          <p className="hero-kicker">ТВОЯ СЛЕДУЮЩАЯ ИСТОРИЯ</p>
          <h1>{game.title}</h1>
          <p className="hero-description">
            {game.short_description ||
              "Откройте новый мир. Узнайте больше о своём следующем приключении."}
          </p>
          <div className="hero-genres">
            {game.genres?.map((g) => (
              <span key={g.id}>{g.name}</span>
            ))}
            <span>Для ПК</span>
          </div>
          <div className="hero-bottom">
            <Link className="button primary" to={`/game/${game.slug}`}>
              Об игре <Icon name="arrow" />
            </Link>
            <Price game={game} />
          </div>
        </div>
        <div className="hero-counter">
          <span>0{(slide % featured.length) + 1}</span> / 0{featured.length}
        </div>
      </section>
      <div className="feature-strip" aria-label="Выбор избранной игры">
        {featured.map((g, i) => (
          <button
            key={g.id}
            className={`feature-item ${slide === i ? "selected" : ""}`}
            onClick={() => setSlide(i)}
            aria-pressed={slide === i}
          >
            {g.cover_image && <img src={g.cover_image} alt="" />}
            <span>
              <small>{"Стоит поиграть"}</small>
              <strong>{g.title}</strong>
            </span>
            <Icon name="chevron" size={17} />
          </button>
        ))}
      </div>
      <section className="store-section">
        <SectionTitle
          eyebrow="Больше игр. Меньше цена."
          title="Особые предложения"
          link="/?view=sale"
        />
        <div className="offers-grid">
          {games
            .filter((g) => g.discount_percent > 0)
            .slice(0, 3)
            .map((g) => (
              <GameCard key={g.id} game={g} />
            ))}
        </div>
      </section>
      <section className="store-section">
        <SectionTitle
          eyebrow="Новые миры ближе, чем кажется"
          title="Вам может понравиться"
        />
        <div className="game-grid">
          {[...games.slice(3), ...games.slice(0, 3)].slice(0, 4).map((g) => (
            <GameCard key={g.id} game={g} />
          ))}
        </div>
      </section>
      <section className="genre-section">
        <div>
          <p className="eyebrow">ИГРАЙТЕ ПО СВОИМ ПРАВИЛАМ</p>
          <h2>
            Какое сегодня
            <br />
            настроение?
          </h2>
        </div>
        <div className="genre-buttons">
          {genres.slice(0, 4).map((g, i) => (
            <Link
              key={g.id}
              to={`/?view=catalog&genre=${encodeURIComponent(g.id)}`}
            >
              <Icon name={["spark", "arrow", "grid", "user"][i]} size={25} />
              <strong>{g.name}</strong>
              <span>Найти свою игру</span>
              <b>↗</b>
            </Link>
          ))}
        </div>
      </section>
      <section className="store-section">
        <SectionTitle title="Стоит добавить в коллекцию" />
        <div className="compact-grid">
          {games.slice(2, 8).map((g) => (
            <Link className="compact-game" key={g.id} to={`/game/${g.slug}`}>
              <img src={g.cover_image} alt="" loading="lazy" />
              <div>
                <h3>{g.title}</h3>
                <p className="game-genre">
                  {g.genres?.map((x) => x.name).join(" · ")}
                </p>
                <Price game={g} />
              </div>
              <Icon name="chevron" size={16} />
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
