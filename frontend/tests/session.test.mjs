import { createServer as createHttpServer } from "node:http";
import assert from "node:assert/strict";
import {before, beforeEach, after, test} from "node:test";
import {createServer} from "vite";
import axios from "axios";
let server, api, refreshApi, state, queryClient, auth, catalog;
const old = "old.payload.signature", fresh = "fresh.payload.signature", refresh = "refresh.payload.signature";
const ok = (config, data = {}) => ({config, data, status: 200, statusText: "OK", headers: {}});
const denied = config => new axios.AxiosError("expired", "ERR_BAD_REQUEST", config, null, {status: 401, data: {detail: "expired"}, config});
before(async () => {
  const memory = new Map();
  globalThis.localStorage = {getItem: key => memory.get(key) ?? null, setItem: (key, value) => memory.set(key, String(value)), removeItem: key => memory.delete(key)};
  server = await createServer({configFile: false, server: {middlewareMode: true, hmr: {server: createHttpServer()}}, appType: "custom"});
  ({api, refreshApi} = await server.ssrLoadModule("/src/api/client.js"));
  ({useAuthStore: state} = await server.ssrLoadModule("/src/store/authStore.js"));
  ({queryClient} = await server.ssrLoadModule("/src/queryClient.js"));
  auth = await server.ssrLoadModule("/src/api/auth.js");
  catalog = await server.ssrLoadModule("/src/api/catalog.js");
});
beforeEach(() => {
  state.getState().logout();
  api.defaults.adapter = async config => ok(config);
  refreshApi.defaults.adapter = async config => ok(config, {access: fresh, refresh});
});
after(async () => { queryClient.clear(); await server.close(); delete globalThis.localStorage; });
test("login rejects HTML and never attaches an existing token", async () => {
  state.getState().setTokens(old, refresh);
  api.defaults.adapter = async config => { assert.equal(config.headers.Authorization, undefined); return ok(config, "<html>fallback</html>"); };
  await assert.rejects(() => auth.login("buyer", "password"), /не подтвердил/);
  assert.equal(state.getState().accessToken, old);
});
test("concurrent 401 requests share exactly one refresh", async () => {
  state.getState().setTokens(old, refresh); let count = 0;
  api.defaults.adapter = async config => { if (config.headers.Authorization === `Bearer ${old}`) throw denied(config); return ok(config); };
  refreshApi.defaults.adapter = async config => { assert.equal(config.url, "/auth/login/refresh/"); count++; await new Promise(resolve => setTimeout(resolve, 5)); return ok(config, {access: fresh, refresh}); };
  await Promise.all([api.get("/library/"), api.get("/store/cart/summary/")]);
  assert.equal(count, 1); assert.equal(state.getState().accessToken, fresh);
});
test("refresh cannot restore a logged-out session", async () => {
  state.getState().setTokens(old, refresh); let release, start;
  const ready = new Promise(resolve => { start = resolve; });
  api.defaults.adapter = async config => { throw denied(config); };
  refreshApi.defaults.adapter = config => new Promise(resolve => { release = () => resolve(ok(config, {access: fresh, refresh})); start(); });
  const request = api.get("/library/"); await ready; state.getState().logout(); release();
  await assert.rejects(() => request, /Сессия изменилась/); assert.equal(state.getState().accessToken, null);
});
test("logout clears both private and staff catalog caches", () => {
  queryClient.setQueryData(["library"], {private: true}); queryClient.setQueryData(["games"], {draft: true});
  state.getState().logout(); assert.equal(queryClient.getQueryCache().getAll().length, 0);
});
test("late response from a previous account is discarded", async () => {
  state.getState().setTokens(old, refresh); let release, start;
  const ready = new Promise(resolve => { start = resolve; });
  api.defaults.adapter = config => new Promise(resolve => { release = () => resolve(ok(config)); start(); });
  const request = api.get("/library/"); await ready; state.getState().setTokens(fresh, refresh); release();
  await assert.rejects(() => request, /Сессия изменилась/);
});
test("refresh denial logs out with no infinite retry", async () => {
  state.getState().setTokens(old, refresh); let count = 0;
  api.defaults.adapter = async config => { throw denied(config); };
  refreshApi.defaults.adapter = async config => { count++; throw denied(config); };
  await assert.rejects(() => api.get("/library/")); assert.equal(count, 1); assert.equal(state.getState().accessToken, null);
});
test("refresh network failure preserves credentials", async () => {
  state.getState().setTokens(old, refresh);
  api.defaults.adapter = async config => { throw denied(config); };
  refreshApi.defaults.adapter = async () => { throw new axios.AxiosError("offline", "ERR_NETWORK"); };
  await assert.rejects(() => api.get("/library/")); assert.equal(state.getState().refreshToken, refresh);
});
test("expired access without refresh retries public GET anonymously once", async () => {
  state.setState({accessToken: old, refreshToken: null}); let count = 0;
  api.defaults.adapter = async config => { count++; if (config.headers.Authorization) throw denied(config); return ok(config, {results: []}); };
  await catalog.getGames(); assert.equal(count, 2); assert.equal(state.getState().accessToken, null);
});
test("HTML catalog response is an error, not empty data", async () => {
  api.defaults.adapter = async config => ok(config, "<html>fallback</html>");
  await assert.rejects(() => catalog.getGames(), /некорректный список/);
});
test("genres load every page without following external next links", async () => {
  api.defaults.adapter = async config => { assert.equal(config.url, "/catalog/genres/"); return ok(config, {results: [{slug: `genre-${config.params.page}`}], next: config.params.page === 1 ? "https://untrusted.invalid/" : null}); };
  assert.equal((await catalog.getGenres()).results.length, 2);
});
