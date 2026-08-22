import { api } from "./client";

export const login = (username, password) =>
  api.post("/auth/login/", { username, password }).then((r) => r.data);
export const register = (payload) => api.post("/auth/register/", payload).then((r) => r.data);
export const getMe = () => api.get("/auth/me/").then((r) => r.data);
