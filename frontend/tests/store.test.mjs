import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { createServer } from "vite";
import {
  validateRegistration,
  registrationErrors,
} from "../src/utils/registration.js";
let server,
  catalog,
  store,
  auth,
  api,
  requests = [],
  response;
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
  ({ api } = await server.ssrLoadModule("/src/api/client.js"));
  api.defaults.adapter = async (config) => {
    requests.push(config);
    if (response instanceof Error) throw response;
    return {
      data: response,
      status: 200,
      statusText: "OK",
      headers: {},
      config,
    };
  };
  catalog = await server.ssrLoadModule("/src/api/catalog.js");
  store = await server.ssrLoadModule("/src/api/store.js");
  auth = await server.ssrLoadModule("/src/api/auth.js");
});
after(async () => {
  await server?.close();
  delete globalThis.localStorage;
});
test("empty backend catalog stays empty and filters use the Django contract", async () => {
  response = { results: [], count: 0, next: null, previous: null };
  assert.deepEqual(
    await catalog.getGames({
      genres: "7",
      search: "query",
      ordering: "-created_at",
    }),
    response,
  );
  assert.deepEqual(requests.at(-1).params, {
    genres: "7",
    search: "query",
    ordering: "-created_at",
  });
  assert.equal(requests.at(-1).url, "/catalog/games/");
});
test("server failure is not replaced with demo games", async () => {
  response = new Error("offline");
  await assert.rejects(() => catalog.getGames(), /offline/);
});
test("cart and library use backend data and cart additions send a game ID", async () => {
  response = { results: [] };
  assert.deepEqual(await store.getCart(), response);
  assert.equal(requests.at(-1).url, "/store/cart/");
  await store.addToCart("server-game-id");
  assert.deepEqual(JSON.parse(requests.at(-1).data), {
    game: "server-game-id",
  });
  await store.getLibrary();
  assert.equal(requests.at(-1).url, "/library/");
});
test("registration sends only fields accepted by Django", async () => {
  response = { id: "created-user" };
  const result = await auth.register({
    username: "tester",
    email: "test@example.com",
    password: "sample-password",
    confirmPassword: "sample-password",
  });
  assert.deepEqual(result, response);
  assert.equal(requests.at(-1).url, "/auth/register/");
  assert.deepEqual(JSON.parse(requests.at(-1).data), {
    username: "tester",
    email: "test@example.com",
    password: "sample-password",
  });
});
test("registration catches invalid fields and a mismatched password before submission", () => {
  assert.deepEqual(
    Object.keys(
      validateRegistration({
        username: " ",
        email: "bad",
        password: "short",
        confirmPassword: "different",
      }),
    ),
    ["username", "email", "password", "confirmPassword"],
  );
  assert.deepEqual(
    validateRegistration({
      username: "player",
      email: "player@example.com",
      password: "12345678",
      confirmPassword: "12345678",
    }),
    {},
  );
});
test("registration exposes field errors and handles offline or unstructured responses", () => {
  assert.deepEqual(
    registrationErrors({
      response: {
        data: {
          username: ["Этот логин занят."],
          email: ["Некорректный email."],
        },
      },
    }),
    { username: "Этот логин занят.", email: "Некорректный email." },
  );
  assert.equal(
    registrationErrors({
      response: { data: { non_field_errors: ["Регистрация закрыта."] } },
    }).form,
    "Регистрация закрыта.",
  );
  assert.ok(registrationErrors(new Error("offline")).form);
  assert.ok(
    registrationErrors({ response: { data: "<html>Unavailable</html>" } }).form,
  );
});

test('registration does not report success for an HTML fallback page', async () => {
  response = '<html>Frontend fallback</html>';
  await assert.rejects(() => auth.register({username:'tester',email:'test@example.com',password:'sample-password'}), /Сервер не подтвердил/);
});
