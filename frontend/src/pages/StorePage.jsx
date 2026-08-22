import { useQuery } from "@tanstack/react-query";
import { getGames } from "../api/catalog";
import GameCard from "../components/GameCard";

export default function StorePage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["games"],
    queryFn: () => getGames(),
  });

  if (isLoading) return <p>Загрузка...</p>;
  if (error) return <p>Ошибка загрузки каталога</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Витрина</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {data?.results?.map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </div>
    </div>
  );
}
