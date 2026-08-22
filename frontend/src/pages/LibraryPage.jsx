import { useQuery } from "@tanstack/react-query";
import { getLibrary } from "../api/store";

export default function LibraryPage() {
  const { data, isLoading } = useQuery({ queryKey: ["library"], queryFn: getLibrary });

  if (isLoading) return <p>Загрузка...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Моя библиотека</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {data?.results?.map((entry) => (
          <div key={entry.id} className="bg-slate-800 p-3 rounded">
            {entry.game.title}
          </div>
        ))}
      </div>
    </div>
  );
}
