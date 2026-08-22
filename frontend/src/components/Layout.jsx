import { Outlet, Link } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export default function Layout() {
  const { accessToken, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="flex items-center justify-between px-6 py-4 bg-slate-800">
        <Link to="/" className="text-xl font-bold">GD-Store</Link>
        <nav className="flex gap-4 text-sm">
          <Link to="/">Магазин</Link>
          <Link to="/library">Библиотека</Link>
          <Link to="/cart">Корзина</Link>
          {accessToken ? (
            <button onClick={logout}>Выйти</button>
          ) : (
            <>
              <Link to="/login">Войти</Link>
              <Link to="/register">Регистрация</Link>
            </>
          )}
        </nav>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
}
