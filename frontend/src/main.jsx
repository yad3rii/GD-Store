import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { useQuery, QueryClientProvider } from "@tanstack/react-query";
import App from "./App.jsx";
import { useAuthStore } from "./store/authStore";
import { getMe } from "./api/auth";
function SessionApp() {
  const {sessionId, accessToken} = useAuthStore();
  const {data} = useQuery({queryKey: ["me", sessionId], queryFn: getMe, enabled: Boolean(accessToken)});
  React.useEffect(() => { if (data) useAuthStore.getState().sessionId === sessionId && useAuthStore.getState().setUser(data); }, [data, sessionId]);
  return <App key={sessionId} />;
}
import "./index.css";

import { queryClient } from "./queryClient";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <SessionApp />
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
);
