import { api } from "./client";
export const login = (username, password) =>
  api.post("/auth/login/", { username, password }).then((r) => r.data);
export async function register({ username, email, password }) {
  const { data } = await api.post("/auth/register/", { username, email, password });
  if (!data?.id) throw new Error("Сервер не подтвердил создание аккаунта.");
  return data;
}
export const getMe = () => api.get("/auth/me/").then((r) => r.data);
