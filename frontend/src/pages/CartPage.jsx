import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getCart, removeFromCart, checkout } from "../api/store";
import Price, { formatPrice } from "../components/Price";
import Icon from "../components/Icon";
export default function CartPage() {
  const qc = useQueryClient();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["cart"],
    queryFn: getCart,
  });
  const remove = useMutation({
    mutationFn: removeFromCart,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["cart"] }),
  });
  const order = useMutation({ mutationFn: checkout });
  const items = data?.results || [];
  if (isLoading)
    return (
      <div className="empty-state" role="status">
        Загружаем корзину…
      </div>
    );
  if (error)
    return (
      <div className="empty-state" role="alert">
        <h1>Корзина недоступна</h1>
        <p>Войдите в аккаунт и проверьте подключение к серверу.</p>
        <Link className="button primary" to="/login">
          Войти
        </Link>
        <button onClick={() => refetch()}>Повторить</button>
      </div>
    );
  return (
    <section className="catalog-page">
      <p className="eyebrow">Ещё ближе к приключению</p>
      <h1>
        Ваша корзина{" "}
        <span style={{ color: "var(--muted)" }}>({items.length})</span>
      </h1>
      {items.length ? (
        <>
          {items.map((i) => (
            <div className="cart-row" key={i.id}>
              <img src={i.game.cover_image} alt="" />
              <div>
                <Link to={`/game/${i.game.slug}`}>
                  <h3>{i.game.title}</h3>
                </Link>
                <p className="game-genre">Игра для ПК</p>
              </div>
              <Price game={i.game} />
              <button
                className="text-link"
                disabled={remove.isPending}
                onClick={() => remove.mutate(i.id)}
              >
                Удалить
              </button>
            </div>
          ))}
          <div className="cart-summary">
            <div>
              Итого{" "}
              <strong>
                {formatPrice(
                  items.reduce((s, i) => s + Number(i.game.final_price), 0),
                )}
              </strong>
            </div>
            <button
              className="button primary"
              disabled={order.isPending || order.isSuccess}
              onClick={() => order.mutate()}
            >
              Оформить заказ <Icon name="arrow" />
            </button>
          </div>
          {remove.isError && (
            <p role="alert" className="error-message">
              Не удалось удалить игру. Попробуйте снова.
            </p>
          )}
          {order.isError && (
            <p role="alert" className="error-message">
              Не удалось оформить заказ. Попробуйте снова.
            </p>
          )}
          {order.isSuccess && (
            <p role="status" className="status-message">
              Заказ создан. Статус оплаты уточняется на сервере.
            </p>
          )}
        </>
      ) : (
        <div className="empty-state">
          <Icon name="cart" size={42} />
          <h2>Здесь начинается ваша коллекция</h2>
          <p>Добавьте игру, которая вам понравилась.</p>
          <Link to="/" className="button primary">
            Найти игру <Icon name="arrow" />
          </Link>
        </div>
      )}
    </section>
  );
}
