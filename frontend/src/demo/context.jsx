import { createCredential, verify, recoveryKey } from "./auth.mjs";
import { createContext, useContext, useEffect, useState } from "react";
import { load, STORAGE_KEY, transition, seed } from "./model.mjs";
const Context = createContext(null);
export function DemoProvider({ children }) {
  const [state, setState] = useState(() => load(localStorage));
  const [notice, setNotice] = useState("");
  useEffect(() => {
    const listener = (e) => {
      if (e.key === STORAGE_KEY) setState(load(localStorage));
    };
    window.addEventListener("storage", listener);
    return () => window.removeEventListener("storage", listener);
  }, []);
  useEffect(() => {
    if (!notice) return;
    const t = setTimeout(() => setNotice(""), 4500);
    return () => clearTimeout(t);
  }, [notice]);
  function act(action, message) {
    try {
      const next = transition(load(localStorage), action);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setState(next);
      if (message) setNotice(message);
      return true;
    } catch (e) {
      setNotice(
        e.name === "QuotaExceededError"
          ? "Память браузера заполнена. Удалите лишние локальные данные."
          : e.message,
      );
      return false;
    }
  }
  async function account(action) {
    if (action.mode === "register") {
      const code = recoveryKey();
      const credential = await createCredential(action.password, code);
      if (
        !act({
          type: "auth-register",
          name: action.name,
          handle: action.handle,
          email: action.email,
          credential,
        })
      )
        throw Error("Регистрация не выполнена. Проверьте логин и email.");
      return { recovery: code };
    }
    const snapshot = load(localStorage);
    const login = action.login.trim().toLowerCase();
    const user = snapshot.users.find(
      (u) => u.email === login || u.handle === login,
    );
    if (!user?.auth)
      throw Error(
        "Локальная учётная запись не найдена. Готовые демопрофили доступны в настройках.",
      );
    const valid = await verify(
      action.mode === "reset" ? action.recovery : action.password,
      user.auth,
      action.mode === "reset",
    );
    if (!valid)
      throw Error(
        action.mode === "reset"
          ? "Неверный код восстановления."
          : "Неверный логин или пароль.",
      );
    const latest = load(localStorage).users.find((u) => u.id === user.id);
    if (latest?.auth?.hash !== user.auth.hash)
      throw Error("Данные профиля изменились. Повторите попытку.");
    const ok =
      action.mode === "reset"
        ? act({
            type: "auth-reset",
            user: user.id,
            credential: await createCredential(action.password),
          })
        : act({ type: "auth-login", user: user.id });
    if (!ok) throw Error("Действие не выполнено.");
    return {};
  }
  function reset() {
    try {
      const next = load({ getItem: () => JSON.stringify(seed()) });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setState(next);
      setNotice("Демоданные восстановлены");
    } catch {
      setNotice("Не удалось сохранить данные браузера.");
    }
  }
  return (
    <Context.Provider
      value={{
        state,
        me: state.users.find((u) => u.id === state.active),
        act,
        account,
        reset,
        notify: setNotice,
      }}
    >
      {children}
      {notice && (
        <div className="toast" role="status">
          {notice}
          <button
            onClick={() => setNotice("")}
            aria-label="Закрыть уведомление"
          >
            ×
          </button>
        </div>
      )}
    </Context.Provider>
  );
}
export const useDemo = () => useContext(Context);
