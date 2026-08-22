import { api } from "./client";

export const getGames = (params) => api.get("/catalog/games/", { params }).then((r) => r.data);
export const getGame = (slug) => api.get(`/catalog/games/${slug}/`).then((r) => r.data);
export const getGenres = () => api.get("/catalog/genres/").then((r) => r.data);
