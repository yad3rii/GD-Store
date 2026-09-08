import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "vite";
import React from "react";
import { renderToString } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { seed } from "../src/demo/model.mjs";
test("all main routes render without a server or API calls", async () => {
  const server = await createServer({
    server: { middlewareMode: true },
    appType: "custom",
    optimizeDeps: { noDiscovery: true, include: [] },
  });
  const state = seed();
  const originalError = console.error;
  console.error = (message, ...args) => {
    if (
      typeof message === "string" &&
      message.startsWith("Warning: useLayoutEffect does nothing on the server")
    )
      return;
    originalError(message, ...args);
  };
  globalThis.localStorage = { getItem: () => JSON.stringify(state) };
  try {
    const { default: App } = await server.ssrLoadModule("/src/App.jsx");
    for (const path of [
      "/",
      "/profile",
      "/profile/nova",
      "/library",
      "/wishlist",
      "/cart",
      "/game/orbital",
      "/friends",
      "/messages/nova",
      "/community",
      "/community/t1",
      "/workshop",
      "/workshop/w1",
      "/settings",
      "/login",
      "/register",
      "/orders",
      "/missing",
    ]) {
      const html = renderToString(
        React.createElement(
          MemoryRouter,
          { initialEntries: [path] },
          React.createElement(App),
        ),
      );
      assert.ok(html.includes("GD"), "Route failed: " + path);
      assert.equal(
        html.includes("Страница не найдена"),
        path === "/missing",
        "Unexpected fallback: " + path,
      );
      assert.ok(!html.includes("undefined"), "Undefined text: " + path);
    }
  } finally {
    console.error = originalError;
    await server.close();
    delete globalThis.localStorage;
  }
});
