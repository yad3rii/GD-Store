import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getGame } from "../api/catalog";
import { addToCart } from "../api/store";

export default function GamePage() {
  const { slug } = useParams();
  const { data: game, isLoading } = useQuery({
    queryKey: ["game", slug],
    queryFn: () => getGame(slug),
  });
  const addMutation = useMutation({ mutationFn: () => addToCart(game.id) });

  if (isLoading) return <p>Загрузка...</p>;
  if (!game) return <p>Игра не найдена</p>;

  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-bold">{game.title}</h1>
      <p className="text-slate-400 mt-2">{game.short_description}</p>
      <div className="grid grid-cols-3 gap-2 my-4">
        {game.screenshots?.map((s) => (
          <img key={s.id} src={s.image} className="rounded" />
        ))}
      </div>
      <p className="whitespace-pre-line">{game.description}</p>
      <div className="mt-6 flex items-center gap-4">
        <span className="text-xl font-semibold">{game.final_price} ₴</span>
        <button
          onClick={() => addMutation.mutate()}
          className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded"
        >
          В корзину
        </button>
      </div>
    </div>
  );
}
