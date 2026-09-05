import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { createServer } from "vite";
let server, catalog, store;
before(async () => {
  globalThis.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
  };
  server = await createServer({
    configFile: false,
    server: { middlewareMode: true },
    appType: "custom",
  });
  catalog = await server.ssrLoadModule("/src/api/catalog.js");
  store = await server.ssrLoadModule("/src/api/store.js");
});
after(async () => {
  await server?.close();
  delete globalThis.localStorage;
});
test("catalog supports case-insensitive search and genre filtering", async () => {
  assert.equal(
    (await catalog.getGames({ search: "CYBERPUNK" })).results[0].slug,
    "cyberpunk-2077",
  );
  const result = await catalog.getGames({ genres__slug: "Экшен" });
  assert.ok(result.results.length);
  assert.ok(
    result.results.every((g) => g.genres.some((x) => x.slug === "Экшен")),
  );
  assert.equal(
    (await catalog.getGames({ search: "not-a-real-game" })).count,
    0,
  );
});
test("catalog sorts prices without mutating the default selection", async () => {
  const before = await catalog.getGames();
  const sorted = await catalog.getGames({ ordering: "price" });
  assert.ok(sorted.results.every((g, i, a) => !i || a[i - 1].price <= g.price));
  assert.deepEqual((await catalog.getGames()).results, before.results);
});
test("game lookup handles missing slugs", async () => {
  await assert.rejects(() => catalog.getGame("missing"));
});
test("cart deduplicates additions, removes items and never processes demo payments", async () => {
  const game = await catalog.getGame("cyberpunk-2077");
  await store.addToCart(game.id);
  await store.addToCart(game.id);
  assert.equal((await store.getCart()).results.length, 1);
  await assert.rejects(() => store.addToCart("missing"));
  assert.equal((await store.getCart()).results.length, 1);
  await assert.rejects(() => store.checkout());
  await store.removeFromCart(game.id);
  assert.equal((await store.getCart()).results.length, 0);
});
