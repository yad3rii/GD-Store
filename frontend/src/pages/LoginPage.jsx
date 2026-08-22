import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/auth";
import { useAuthStore } from "../store/authStore";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const setTokens = useAuthStore((s) => s.setTokens);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = await login(username, password);
    setTokens(data.access, data.refresh);
    navigate("/");
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-sm flex flex-col gap-3">
      <h1 className="text-2xl font-bold">Вход</h1>
      <input
        className="bg-slate-800 p-2 rounded"
        placeholder="Логин"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        className="bg-slate-800 p-2 rounded"
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="bg-blue-600 hover:bg-blue-500 py-2 rounded">Войти</button>
    </form>
  );
}
