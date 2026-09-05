import { Outlet, Link, NavLink, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuthStore } from "../store/authStore";
import Icon from "./Icon";
import { demoMode } from "../data/demo";
export default function Layout() {
  const { accessToken, logout } = useAuthStore();
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  return (
    <div className="site-shell">
      <a href="#main" className="skip-link">
        Перейти к содержимому
      </a>
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" className="brand">
            <span className="brand-mark">G↗</span>
            <span>
              GD<span className="brand-light">STORE</span>
              <small>YOUR NEXT ADVENTURE</small>
            </span>
          </Link>
          <nav className="primary-nav" aria-label="Основная навигация">
            <NavLink to="/" end>
              <Icon name="grid" />
              Магазин
            </NavLink>
            <NavLink to="/library">
              <Icon name="library" />
              Библиотека
            </NavLink>
          </nav>
          <div className="header-actions">
            <Link className="icon-button" to="/cart" aria-label="Корзина">
              <Icon name="cart" />
            </Link>
            <span className="header-divider" />
            {accessToken ? (
              <button className="account-button" onClick={logout}>
                Выйти
              </button>
            ) : (
              <Link className="account-button" to="/login">
                <Icon name="user" />
                Войти
              </Link>
            )}
          </div>
        </div>
      </header>
      <div className="store-toolbar">
        <nav aria-label="Каталог">
          <Link to="/">Обзор</Link>
          <Link to="/?view=catalog">Каталог игр</Link>
          <Link to="/?view=sale">
            Скидки <i className="tiny-dot" />
          </Link>
          <Link to="/?view=catalog&genre=Ролевые">Категории</Link>
        </nav>
        <form
          className="search"
          role="search"
          onSubmit={(e) => {
            e.preventDefault();
            navigate(`/?view=catalog&search=${encodeURIComponent(search)}`);
          }}
        >
          <Icon name="search" size={18} />
          <input
            aria-label="Найти игру"
            placeholder="Найти свою следующую игру"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <kbd>↵</kbd>
        </form>
      </div>
      <main id="main" className="main-content">
        <Outlet />
      </main>
      <footer className="footer">
        <Link to="/" className="footer-brand">
          GD STORE<span>Игра начинается здесь.</span>
        </Link>
        <div>
          {demoMode && (
            <p className="demo-note">
              Демо-витрина · цены и предложения приведены для примера
            </p>
          )}
          <p>
            © {new Date().getFullYear()} GD Store. Изображения игр принадлежат
            их правообладателям.
          </p>
        </div>
        <a href="#main" className="back-top">
          Наверх ↑
        </a>
      </footer>
    </div>
  );
}
