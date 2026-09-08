import { api } from "./client";
import { pageData } from "./contracts";
export const getGames = (params = {}, {signal} = {}) => api.get("/catalog/games/", {params, signal}).then(r => pageData(r.data));
export const getGame = (slug, {signal} = {}) => api.get(`/catalog/games/${encodeURIComponent(slug)}/`, {signal}).then(({data}) => {
  if (!data?.id || !data?.slug) throw new Error("Сервер вернул некорректную игру.");
  return data;
});
export async function getGenres({signal} = {}) {
  const results = [];
  for (let page = 1; ; page++) {
    const {data} = await api.get("/catalog/genres/", {params: {page}, signal});
    const current = pageData(data);
    results.push(...current.results);
    if (!current.next) return {results};
    if (!current.results.length) throw new Error("Некорректная пагинация жанров.");
  }
}
