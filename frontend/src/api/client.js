import axios from "axios";
import { useAuthStore } from "../store/authStore";

export const api = axios.create({ baseURL: "/api/v1" });

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// TODO: interceptor для 401 -> обновление токена через /auth/login/refresh/
