import { api } from "./client";
import { pageData } from "./contracts";
export const getCart = ({signal} = {}) => api.get("/store/cart/summary/", {signal}).then(({data}) => {
  pageData(data);
  if (typeof data.checkout_token !== "string" || !Number.isFinite(Number(data.total))) throw new Error("Не удалось подтвердить состав корзины.");
  return data;
});
export const addToCart = (gameId) => api.post("/store/cart/", {game: gameId}).then(r => r.data);
export const removeFromCart = (id) => api.delete(`/store/cart/${encodeURIComponent(id)}/`);
export const checkout = (checkoutToken) => api.post("/store/cart/checkout/", {checkout_token: checkoutToken}).then(({data}) => {
  if (!data?.id) throw new Error("Сервер не подтвердил заказ.");
  return data;
});
export const getLibrary = (page = 1, {signal} = {}) => api.get("/library/", {params: {page}, signal}).then(r => pageData(r.data));
