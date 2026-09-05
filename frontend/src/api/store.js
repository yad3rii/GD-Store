import { api } from "./client";
export const getCart = () => api.get("/store/cart/").then((r) => r.data);
export const addToCart = (gameId) =>
  api.post("/store/cart/", { game: gameId }).then((r) => r.data);
export const removeFromCart = (id) =>
  api.delete(`/store/cart/${encodeURIComponent(id)}/`);
export const checkout = () =>
  api.post("/store/cart/checkout/").then((r) => r.data);
export const getLibrary = () => api.get("/library/").then((r) => r.data);
