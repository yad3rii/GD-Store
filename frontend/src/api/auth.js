import { api } from "./client";
import { validToken } from "../store/authStore";
export async function login(username, password) {
  const {data} = await api.post("/auth/login/", {username, password}, {skipAuth: true});
  if (!validToken(data?.access) || !validToken(data?.refresh)) throw new Error("Сервер не подтвердил вход.");
  return data;
}
export async function register({username, email, password}) {
  const {data} = await api.post("/auth/register/", {username, email, password}, {skipAuth: true});
  if (!data?.id) throw new Error("Сервер не подтвердил создание аккаунта.");
  return data;
}
export async function getMe({signal} = {}) {
  const {data} = await api.get("/auth/me/", {signal});
  if (!data?.id) throw new Error("Сервер не подтвердил профиль.");
  return data;
}
