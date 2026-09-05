import { api } from "./client";
import { demoGames, demoMode } from "../data/demo";
export async function getGames(params = {}) {
  if (!demoMode) return (await api.get("/catalog/games/", { params })).data;
  let results = demoGames.filter(
    (g) =>
      (!params.search ||
        g.title.toLowerCase().includes(params.search.toLowerCase())) &&
      (!params.genres__slug ||
        g.genres.some((x) => x.slug === params.genres__slug)),
  );
  if (params.ordering === "price") results.sort((a, b) => a.price - b.price);
  if (params.ordering === "-price") results.sort((a, b) => b.price - a.price);
  if (params.ordering === "title")
    results.sort((a, b) => a.title.localeCompare(b.title));
  return { count: results.length, results, next: null, previous: null };
}
export async function getGame(slug) {
  if (!demoMode) return (await api.get(`/catalog/games/${slug}/`)).data;
  const game = demoGames.find((g) => g.slug === slug);
  if (!game) throw Error("Игра не найдена");
  return game;
}
export const getGenres = () =>
  demoMode
    ? Promise.resolve([
        ...new Map(
          demoGames.flatMap((g) => g.genres).map((g) => [g.id, g]),
        ).values(),
      ])
    : api.get("/catalog/genres/").then((r) => r.data);
