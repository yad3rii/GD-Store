export const formatPrice = (value) =>
  new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "UAH",
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
export default function Price({ game }) {
  return (
    <div className="price">
      {game.discount_percent > 0 && (
        <>
          <span className="discount">−{game.discount_percent}%</span>
          <del>{formatPrice(game.price)}</del>
        </>
      )}
      <strong>
        {Number(game.final_price) === 0
          ? "Бесплатно"
          : formatPrice(game.final_price)}
      </strong>
    </div>
  );
}
