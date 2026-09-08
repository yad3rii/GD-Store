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
  function reset() {
    try {
      const next = seed();
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
