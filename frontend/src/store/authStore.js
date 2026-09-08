import { create } from "zustand";
export const validToken = (value) => typeof value === "string" && value.split(".").length === 3 && value.split(".").every(Boolean);
const read = (key) => { try { const value = localStorage.getItem(key); return validToken(value) ? value : null; } catch { return null; } };
const write = (key, value) => { try { value ? localStorage.setItem(key, value) : localStorage.removeItem(key); } catch { /* Session remains usable in memory. */ } };
export const useAuthStore = create((set, get) => ({
  accessToken: read("access"), refreshToken: read("refresh"), user: null, sessionId: 0,
  setTokens: (access, refresh) => {
    if (!validToken(access) || !validToken(refresh)) throw new Error("Сервер не вернул корректные токены.");
    write("access", access); write("refresh", refresh);
    set({accessToken: access, refreshToken: refresh, user: null, sessionId: get().sessionId + 1});
  },
  refreshTokens: (access, refresh, sessionId) => {
    if (get().sessionId !== sessionId) return false;
    if (!validToken(access) || !validToken(refresh)) throw new Error("Некорректный ответ обновления сессии.");
    write("access", access); write("refresh", refresh);
    set({accessToken: access, refreshToken: refresh}); return true;
  },
  setUser: (user) => set({user}),
  logout: () => {
    write("access", null); write("refresh", null);
    set({accessToken: null, refreshToken: null, user: null, sessionId: get().sessionId + 1});
  },
}));
