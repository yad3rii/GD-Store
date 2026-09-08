import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDemo } from "../demo/context";
import { games } from "../demo/model.mjs";
import { Head, Avatar, Gate, Empty, money } from "./Studio";
import { Modal, date } from "./Personal";
export function Account({ register = false }) {
  const { state, act } = useDemo();
  const [name, setName] = useState(""),
    [handle, setHandle] = useState("");
  const nav = useNavigate();
  return (
    <div className="account-layout">
      <div className="account-intro">
        <p className="eyebrow">YOUR PLAYER IDENTITY</p>
        <h1>
          Все твои миры.
          <br />
          Один профиль.
        </h1>
        <p>Библиотека, друзья и любимые сообщества — в одном пространстве.</p>
        <div className="account-emblem">G↗</div>
      </div>
      <section className="panel account-form">
        <h2>{register ? "Создать локальный профиль" : "С возвращением"}</h2>
        <p className="muted space">
          Демонстрация без сервера: пароли и настоящая авторизация не
          используются.
        </p>
        {register ? (
          <form
            className="form-stack space"
            onSubmit={(e) => {
              e.preventDefault();
              if (act({ type: "register", name, handle }, "Профиль создан"))
                nav("/profile");
            }}
          >
            <label>
              Имя игрока
              <input
                required
                maxLength={40}
                autoComplete="nickname"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <label>
              Логин
              <input
                required
                pattern="[A-Za-z0-9_]{3,20}"
                title="3–20 латинских букв, цифр или _"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                maxLength={20}
              />
            </label>
            <button className="btn primary">Создать профиль</button>
            <Link className="accent" to="/login">
              Уже есть локальный профиль?
            </Link>
          </form>
        ) : (
          <>
            <div className="account-choices">
              {state.users.map((u) => (
                <button
                  key={u.id}
                  onClick={() => {
                    if (
                      act(
                        { type: "switch", user: u.id },
                        "Вы вошли как " + u.name,
                      )
                    )
                      nav("/profile");
                  }}
                >
                  <Avatar user={u} />
                  <span>
                    {u.name}
                    <small>@{u.handle}</small>
                  </span>
                  <span>→</span>
                </button>
              ))}
            </div>
            <Link className="btn primary" to="/register">
              Создать свой профиль
            </Link>
          </>
        )}
      </section>
    </div>
  );
}
export function Settings() {
  const { state, me, act, reset } = useDemo();
  const [confirm, setConfirm] = useState(false);
  const nav = useNavigate();
  const settings = state.settings[me?.id] || {};
  return (
    <>
      <Head
        eyebrow="MAKE IT YOURS"
        title="Настройки пространства"
        text="Оформление, демопрофили и ваши локальные данные."
      />
      <div className="settings-grid">
        <section className="panel">
          <h2>Локальный профиль</h2>
          <p className="muted space">
            Переключитесь на друга, чтобы принять заявку или ответить на
            сообщение. Выбранный профиль общий для вкладок этого сайта.
          </p>
          <div className="account-choices">
            {state.users.map((u) => (
              <button
                key={u.id}
                onClick={() =>
                  act(
                    { type: "switch", user: u.id },
                    "Выбран профиль " + u.name,
                  )
                }
              >
                <Avatar user={u} />
                <span>
                  {u.name}
                  <small>@{u.handle}</small>
                </span>
                <span className="accent">{u.id === me?.id ? "✓" : "→"}</span>
              </button>
            ))}
          </div>
          <Link className="btn" to="/register">
            ＋ Новый профиль
          </Link>
        </section>
        <div>
          <section className="panel">
            <h2>Оформление</h2>
            <Gate>
              <div className="setting-row">
                <div>
                  <strong>Компактный интерфейс</strong>
                  <p className="muted">Меньше отступы в карточках и списках</p>
                </div>
                <input
                  type="checkbox"
                  aria-label="Компактный интерфейс"
                  checked={!!settings.compact}
                  onChange={(e) =>
                    act({
                      type: "settings",
                      values: { compact: e.target.checked },
                    })
                  }
                />
              </div>
              <div className="setting-row">
                <div>
                  <strong>Меньше движения</strong>
                  <p className="muted">Отключить эффекты наведения</p>
                </div>
                <input
                  type="checkbox"
                  aria-label="Отключить анимации"
                  checked={!!settings.motionOff}
                  onChange={(e) =>
                    act({
                      type: "settings",
                      values: { motionOff: e.target.checked },
                    })
                  }
                />
              </div>
              <Link className="btn" to="/profile">
                Изменить профиль
              </Link>
            </Gate>
          </section>
          <section className="panel space">
            <h2>Данные демонстрации</h2>
            <p className="muted space">
              Изменения сохраняются в этом браузере. Реальных аккаунтов, сетевой
              переписки, платежей и загрузки игр нет.
            </p>
            <button
              className="btn danger space"
              onClick={() => setConfirm(true)}
            >
              Сбросить демоданные
            </button>
          </section>
        </div>
      </div>
      {confirm && (
        <Modal
          title="Сбросить локальные изменения?"
          onClose={() => setConfirm(false)}
        >
          <p className="muted">
            Будут удалены созданные здесь профили, сообщения, заявки, обсуждения
            и демозаказы. Исходные примеры восстановятся.
          </p>
          <div className="actions space">
            <button className="btn" onClick={() => setConfirm(false)}>
              Отмена
            </button>
            <button
              className="btn danger"
              onClick={() => {
                reset();
                setConfirm(false);
                nav("/");
              }}
            >
              Сбросить
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
export function Orders() {
  const { state, me } = useDemo();
  const orders = state.orders.filter((o) => o.user === me?.id);
  return (
    <Gate>
      <Head
        eyebrow="ВАШИ ПОКУПКИ"
        title="История демозаказов"
        text="Список локальных заказов. Оплата не выполнялась."
      />
      {orders.map((o) => (
        <section className="panel order space" key={o.id}>
          <div className="section-title">
            <div>
              <p className="eyebrow">ДЕМОЗАКАЗ / {o.id.slice(0, 8)}</p>
              <h3>{date(o.at)}</h3>
            </div>
            <span className="pill accent">В библиотеке</span>
          </div>
          {o.games.map((id) => (
            <Link className="order-game" to={"/game/" + id} key={id}>
              {games.find((g) => g.id === id)?.title}
              <span>↗</span>
            </Link>
          ))}
          <div className="order-total">
            <span>Демонстрационная сумма</span>
            <strong>{money(o.total)}</strong>
          </div>
        </section>
      ))}
      {!orders.length && (
        <Empty
          title="Здесь будут ваши заказы"
          text="Добавьте игру в корзину и оформите демозаказ."
        />
      )}
    </Gate>
  );
}
