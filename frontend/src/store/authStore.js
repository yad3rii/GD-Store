import { create } from "zustand";

export const useAuthStore = create((set) => ({
  accessToken: localStorage.getItem("access") || null,
  refreshToken: localStorage.getItem("refresh") || null,
  user: null,
  setTokens: (access, refresh) => {
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
    set({ accessToken: access, refreshToken: refresh });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
