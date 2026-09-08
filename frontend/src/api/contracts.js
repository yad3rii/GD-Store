export function pageData(data) {
  if (!data || !Array.isArray(data.results)) throw new Error("Сервер вернул некорректный список.");
  return data;
}
export function apiError(error, fallback) {
  const data = error?.response?.data;
  return typeof data?.detail === "string" ? data.detail : (error?.response?.status === 401 ? "Сессия истекла. Войдите снова." : fallback);
}
