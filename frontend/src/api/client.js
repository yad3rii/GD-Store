import axios from "axios";
import { useAuthStore } from "../store/authStore";
const options = {baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1", timeout: 20000};
export const api = axios.create(options);
export const refreshApi = axios.create(options);
let pendingRefresh = null;
const changedSession = () => new axios.CanceledError("Сессия изменилась.");
api.interceptors.request.use((config) => {
  const state = useAuthStore.getState();
  if (config._session !== undefined && config._session !== state.sessionId) throw changedSession();
  config._session = state.sessionId;
  config._access = config.skipAuth ? null : state.accessToken;
  if (config._access) config.headers.Authorization = `Bearer ${config._access}`;
  else delete config.headers.Authorization;
  return config;
});
api.interceptors.response.use((response) => {
  if (response.config._session !== useAuthStore.getState().sessionId) throw changedSession();
  return response;
}, async (error) => {
  const config = error.config;
  if (!config || config.skipAuth || error.response?.status !== 401) throw error;
  const state = useAuthStore.getState();
  if (config._session !== state.sessionId) throw changedSession();
  if (config._retried) { if (state.accessToken) state.logout(); throw error; }
  config._retried = true;
  if (state.accessToken && state.accessToken !== config._access) return api(config);
  if (!state.refreshToken) {
    if (state.accessToken) state.logout();
    if (config.method === "get") { config._session = useAuthStore.getState().sessionId; return api(config); }
    throw error;
  }
  if (!pendingRefresh || pendingRefresh.sessionId !== state.sessionId) {
    const flight = {sessionId: state.sessionId};
    flight.promise = refreshApi.post("/auth/login/refresh/", {refresh: state.refreshToken}).then(({data}) => {
      if (!useAuthStore.getState().refreshTokens(data?.access, data?.refresh || state.refreshToken, state.sessionId)) throw changedSession();
    }).catch((failure) => {
      // Network outages do not revoke a valid refresh token.
      if (useAuthStore.getState().sessionId === state.sessionId &&
          (failure.response?.status === 401 || failure.response?.status === 400 || !failure.isAxiosError)) {
        useAuthStore.getState().logout();
      }
      throw failure;
    }).finally(() => { if (pendingRefresh === flight) pendingRefresh = null; });
    pendingRefresh = flight;
  }
  await pendingRefresh.promise;
  if (useAuthStore.getState().sessionId !== config._session) throw changedSession();
  return api(config);
});
