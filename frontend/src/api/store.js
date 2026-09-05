import { api } from "./client";
import { demoMode, demoGames } from "../data/demo";
let demoCart = [];
export const getCart = () =>
  demoMode
    ? Promise.resolve({ results: [...demoCart] })
    : api.get("/store/cart/").then((r) => r.data);
export async function addToCart(gameId) {
  if (!demoMode) return (await api.post("/store/cart/", { game: gameId })).data;
  const game = demoGames.find((g) => g.id === gameId);
  if (!game) throw Error("Игра не найдена");
  if (!demoCart.some((i) => i.game.id === gameId))
    demoCart = [...demoCart, { id: gameId, game }];
  return { game };
}
export async function removeFromCart(id) {
  if (!demoMode) return api.delete(`/store/cart/${id}/`);
  demoCart = demoCart.filter((i) => i.id !== id);
}
export const checkout = () =>
  demoMode
    ? Promise.reject(Error("Оплата будет доступна после подключения сервера."))
    : api.post("/store/cart/checkout/").then((r) => r.data);
export const getLibrary = () =>
  demoMode
    ? Promise.resolve({ results: [] })
    : api.get("/library/").then((r) => r.data);
