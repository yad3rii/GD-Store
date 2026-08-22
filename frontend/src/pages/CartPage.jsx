import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getCart, removeFromCart, checkout } from "../api/store";

export default function CartPage() {
  const qc = useQueryClient();
  const { data: cart, isLoading } = useQuery({ queryKey: ["cart"], queryFn: getCart });
  const removeMutation = useMutation({
    mutationFn: removeFromCart,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["cart"] }),
  });
  const checkoutMutation = useMutation({ mutationFn: checkout });

  if (isLoading) return <p>Загрузка...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Корзина</h1>
      {cart?.results?.length ? (
        <>
          {cart.results.map((item) => (
            <div key={item.id} className="flex justify-between py-2 border-b border-slate-700">
              <span>{item.game.title}</span>
              <div className="flex gap-3 items-center">
                <span>{item.game.final_price} ₴</span>
                <button onClick={() => removeMutation.mutate(item.id)} className="text-red-400">
                  Удалить
                </button>
              </div>
            </div>
          ))}
          <button
            onClick={() => checkoutMutation.mutate()}
            className="mt-4 bg-green-600 hover:bg-green-500 px-4 py-2 rounded"
          >
            Оформить заказ
          </button>
        </>
      ) : (
        <p>Корзина пуста</p>
      )}
    </div>
  );
}
