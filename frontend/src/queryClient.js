import { QueryClient } from "@tanstack/react-query";
import { useAuthStore } from "./store/authStore";
export const queryClient = new QueryClient({defaultOptions: {queries: {retry: false}}});
useAuthStore.subscribe((state, previous) => {
  if (state.sessionId !== previous.sessionId) {
    void queryClient.cancelQueries();
    queryClient.clear();
  }
});
