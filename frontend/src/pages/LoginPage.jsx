import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import { useAuthStore } from "../store/authStore";
import { demoMode } from "../data/demo";
export default function LoginPage() {
  const [username, setUsername] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState(""),
    [pending, setPending] = useState(false);
  const setTokens = useAuthStore((s) => s.setTokens),
    navigate = useNavigate();
  const submit = async (e) => {
    e.preventDefault();
    if (demoMode) return;
    setPending(true);
    setError("");
    try {
      const data = await login(username, password);
      setTokens(data.access, data.refresh);
      navigate("/");
    } catch {
      setError("Не удалось войти. Проверьте данные и доступность сервера.");
    } finally {
      setPending(false);
    }
  };
  return (
    <form className="auth-panel" onSubmit={submit}>
      <p className="eyebrow">С возвращением</p>
      <h1>Войти в GD Store</h1>
      {demoMode && (
        <p>
          Демо-режим. Авторизация станет доступна после подключения сервера.
        </p>
      )}
      <label>
        Логин
        <input
          autoComplete="username"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </label>
      <label>
        Пароль
        <input
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      {error && (
        <p role="alert" className="error-message">
          {error}
        </p>
      )}
      <button className="button primary" disabled={demoMode || pending}>
        {pending ? "Входим…" : "Войти"}
      </button>
      <Link to="/" className="text-link">
        ← Вернуться в магазин
      </Link>
    </form>
  );
}
