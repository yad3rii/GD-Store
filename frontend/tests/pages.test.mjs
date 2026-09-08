import assert from "node:assert/strict";
import {before, after, test} from "node:test";
import {createServer} from "vite";
import {createServer as createHttpServer} from "node:http";
import React from "react";
import {renderToStaticMarkup} from "react-dom/server";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {StaticRouter} from "react-router-dom/server.js";
let server, state, Store, Cart, Library;
before(async () => {
  globalThis.localStorage = {getItem: () => "test.payload.signature", setItem: () => {}, removeItem: () => {}};
  server = await createServer({configFile: false, esbuild: {jsx: "automatic"}, server: {middlewareMode: true, hmr: {server: createHttpServer()}}, appType: "custom"});
  ({useAuthStore: state} = await server.ssrLoadModule("/src/store/authStore.js"));
  ({default: Store} = await server.ssrLoadModule("/src/pages/StorePage.jsx"));
  ({default: Cart} = await server.ssrLoadModule("/src/pages/CartPage.jsx"));
  ({default: Library} = await server.ssrLoadModule("/src/pages/LibraryPage.jsx"));
});
after(async () => { await server.close(); delete globalThis.localStorage; });
const game = i => ({id: `g${i}`, slug: `game-${i}`, title: `VisibleGame${i}`, price: "10.00", final_price: "10.00", genres: [], tags: []});
function render(Page, location, data) {
  const client = new QueryClient({defaultOptions: {queries: {staleTime: Infinity}}});
  for (const [key, value] of data) client.setQueryData(key, value);
  try { return renderToStaticMarkup(React.createElement(QueryClientProvider, {client}, React.createElement(StaticRouter, {location}, React.createElement(Page)))); }
  finally { client.clear(); }
}
test("catalog renders genre slug as actual dropdown value", () => {
  const html = render(Store, "/?view=catalog", [
    [["games", state.getState().sessionId, "", "", "", 1, false], {results: [game(1)]}],
    [["genres"], {results: [{id: 7, slug: "action", name: "Action"}]}],
  ]);
  assert.match(html, /value="action"/); assert.doesNotMatch(html, /value="7"/);
});
test("cart renders item 21 and server summary rather than truncating to 20", () => {
  const html = render(Cart, "/cart", [[["cart", state.getState().sessionId], {
    results: Array.from({length: 21}, (_, i) => ({id: i, game: game(i)})), total: "210.00", can_checkout: true, checkout_token: "signed",
  }]]);
  assert.match(html, /VisibleGame20/); assert.match(html, /210/);
});
test("library exposes navigation when the backend has another page", () => {
  const html = render(Library, "/library", [[["library", state.getState().sessionId, 1], {results: [{id: 1, game: game(1)}], next: "page2", previous: null}]]);
  assert.match(html, /Далее/); assert.match(html, /Страница 1/);
});
