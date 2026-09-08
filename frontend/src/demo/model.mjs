export const STORAGE_KEY = "gd-store-studio-v1";
export const people = [
  {
    id: "karim",
    name: "Karim",
    handle: "karim",
    initials: "KA",
    color: "#49dcc8",
    status: "online",
    bio: "Собираю миры, в которых хочется остаться. RPG, инди и хороший кооператив.",
    country: "Украина",
    level: 24,
  },
  {
    id: "nova",
    name: "Nova",
    handle: "nova",
    initials: "NO",
    color: "#bba2ff",
    status: "playing",
    bio: "Ещё один забег — и спать.",
    country: "",
    level: 18,
  },
  {
    id: "alex",
    name: "Alex",
    handle: "alex",
    initials: "AL",
    color: "#ffb979",
    status: "online",
    bio: "Всегда за кооператив.",
    country: "",
    level: 31,
  },
  {
    id: "mika",
    name: "Mika",
    handle: "mika",
    initials: "MI",
    color: "#f295ba",
    status: "offline",
    bio: "Охочусь за красивыми скриншотами.",
    country: "",
    level: 12,
  },
  {
    id: "danya",
    name: "Danya",
    handle: "danya",
    initials: "DA",
    color: "#8eafff",
    status: "online",
    bio: "Стратегии и строительство миров.",
    country: "",
    level: 22,
  },
];
export const games = [
  {
    id: "orbital",
    title: "ORBITAL",
    tagline: "За пределами знакомого",
    genre: "Приключения",
    tags: ["Космос", "Открытый мир", "Одиночная"],
    price: 899,
    discount: 35,
    image: "/art/orbital.png",
    color: "#2b7e85",
    rating: 96,
    developer: "Northstar Studio",
    description:
      "Отправьтесь к далёким кольцам Элиона. Исследуйте заброшенные станции, прокладывайте свой маршрут среди звёзд и узнайте, что осталось от первой экспедиции.",
    hours: 42,
    achievements: 12,
    totalAchievements: 32,
  },
  {
    id: "ashen",
    title: "ASHEN CROWN",
    tagline: "У каждого королевства есть тень",
    genre: "RPG",
    tags: ["Фэнтези", "Souls-like", "Одиночная"],
    price: 1299,
    discount: 20,
    image: "/art/ashen.png",
    color: "#9b4545",
    rating: 94,
    developer: "Ember Works",
    description:
      "Пепельное королевство ждёт нового странника. Освойте оружие, исследуйте древние соборы и решите судьбу погасшего солнца.",
    hours: 18,
    achievements: 7,
    totalAchievements: 40,
  },
  {
    id: "velocity",
    title: "VELOCITY / 2099",
    tagline: "Город живёт после полуночи",
    genre: "Гонки",
    tags: ["Киберпанк", "Гонки", "Мультиплеер"],
    price: 699,
    discount: 0,
    image: "/art/velocity.png",
    color: "#624295",
    rating: 91,
    developer: "Nightlane",
    description:
      "Неоновые улицы, ночной дождь и идеальная траектория. Настраивайте автомобиль и открывайте новые районы футуристического мегаполиса.",
    hours: 9,
    achievements: 3,
    totalAchievements: 24,
  },
  {
    id: "echoes",
    title: "ECHOES OF ELION",
    tagline: "Истории далёкой планеты",
    genre: "Инди",
    tags: ["Исследование", "Атмосфера", "Одиночная"],
    price: 399,
    discount: 50,
    image: "/art/orbital.png",
    color: "#318c83",
    rating: 98,
    developer: "Small Worlds",
    description:
      "Неспешное путешествие по следам исчезнувшей цивилизации. Слушайте планету, собирайте воспоминания и находите красоту в тишине.",
    hours: 0,
    achievements: 0,
    totalAchievements: 18,
  },
  {
    id: "hollow",
    title: "HOLLOW KINGDOM",
    tagline: "Постройте свою легенду",
    genre: "Стратегии",
    tags: ["Строительство", "Фэнтези", "Стратегия"],
    price: 799,
    discount: 15,
    image: "/art/ashen.png",
    color: "#945d39",
    rating: 89,
    developer: "Copper Gate",
    description:
      "Возродите город на границе забытых земель. Выбирайте союзников, управляйте ресурсами и защитите своих жителей.",
    hours: 0,
    achievements: 0,
    totalAchievements: 30,
  },
  {
    id: "nightshift",
    title: "NIGHTSHIFT",
    tagline: "Встречаемся на старте",
    genre: "Экшен",
    tags: ["Кооператив", "Киберпанк", "Экшен"],
    price: 0,
    discount: 0,
    image: "/art/velocity.png",
    color: "#794b9c",
    rating: 92,
    developer: "Nightlane",
    description:
      "Кооперативные задания в городе будущего. Соберите команду, выберите маршрут и заберите контракт раньше конкурентов.",
    hours: 0,
    achievements: 0,
    totalAchievements: 20,
  },
];
export const price = (g) => Math.round(g.price * (1 - g.discount / 100));
export function seed() {
  return {
    version: 1,
    active: "karim",
    users: people,
    library: { karim: ["orbital", "ashen", "velocity"] },
    wishlist: { karim: ["echoes"] },
    cart: {},
    friends: [
      { id: "f1", from: "karim", to: "nova", status: "accepted" },
      { id: "f2", from: "karim", to: "alex", status: "accepted" },
      { id: "f3", from: "mika", to: "karim", status: "pending" },
    ],
    messages: [
      {
        id: "m1",
        from: "nova",
        to: "karim",
        text: "Привет! Как тебе новая локация в ORBITAL?",
        at: "2026-09-08T14:00:00Z",
      },
      {
        id: "m2",
        from: "karim",
        to: "nova",
        text: "Очень красиво. Давай вечером исследуем станцию?",
        at: "2026-09-08T14:02:00Z",
      },
    ],
    topics: [
      {
        id: "t1",
        author: "nova",
        game: "orbital",
        title: "Что находится за кольцами Элиона?",
        body: "Нашла необычный сигнал на краю карты. Кто уже добирался до исследовательской станции?",
        replies: [
          {
            id: "r1",
            author: "alex",
            text: "Загляни в обсерваторию — там есть подсказка.",
            at: "2026-09-08T12:30:00Z",
          },
        ],
        at: "2026-09-08T12:00:00Z",
      },
      {
        id: "t2",
        author: "danya",
        game: "ashen",
        title: "Ваше любимое оружие для первого прохождения",
        body: "Пока играю с копьём. Поделитесь сборками без сюжетных спойлеров.",
        replies: [],
        at: "2026-09-08T11:00:00Z",
      },
    ],
    mods: [
      {
        id: "w1",
        author: "nova",
        game: "orbital",
        title: "Elion / Cinematic skies",
        description:
          "Новая цветовая палитра неба и мягкий кинематографичный свет.",
        category: "Визуал",
        version: "1.2",
        subscribers: 1284,
      },
      {
        id: "w2",
        author: "alex",
        game: "ashen",
        title: "The forgotten armoury",
        description: "Концепция набора доспехов забытой королевской стражи.",
        category: "Предметы",
        version: "1.0",
        subscribers: 862,
      },
      {
        id: "w3",
        author: "danya",
        game: "velocity",
        title: "Midnight district",
        description: "Концепция ночной трассы через старый район города.",
        category: "Карты",
        version: "2.0",
        subscribers: 2106,
      },
    ],
    subscriptions: {},
    orders: [],
    reviews: [],
    settings: {},
    activity: [],
  };
}
export function load(storage) {
  try {
    const x = JSON.parse(storage.getItem(STORAGE_KEY));
    return x?.version === 1 && Array.isArray(x.users) ? x : seed();
  } catch {
    return seed();
  }
}
export function transition(s, a) {
  const n = structuredClone(s),
    me = n.active,
    id = a.id || globalThis.crypto.randomUUID(),
    at = new Date().toISOString();
  const need = () => {
    if (!me) throw Error("Выберите профиль, чтобы продолжить.");
  };
  const list = (field) => n[field][me] || (n[field][me] = []);
  const friend = (user) =>
    n.friends.find(
      (f) => [f.from, f.to].includes(me) && [f.from, f.to].includes(user),
    );
  const note = (text) => n.activity.unshift({ id, author: me, text, at });
  switch (a.type) {
    case "switch":
      if (a.user !== null && !n.users.some((u) => u.id === a.user))
        throw Error("Профиль не найден.");
      n.active = a.user;
      break;
    case "register": {
      const handle = a.handle.trim().toLowerCase();
      if (!/^[a-z0-9_]{3,20}$/.test(handle))
        throw Error("Логин: 3–20 латинских букв, цифр или _.");
      if (n.users.some((u) => u.handle === handle)) throw Error("Логин занят.");
      const name = a.name.trim();
      if (!name || name.length > 40) throw Error("Имя: от 1 до 40 символов.");
      n.users.push({
        id,
        handle,
        name,
        initials: name.slice(0, 2).toUpperCase(),
        color: "#49dcc8",
        status: "online",
        bio: "",
        country: "",
        level: 1,
      });
      n.active = id;
      break;
    }
    case "profile":
      need();
      Object.assign(
        n.users.find((u) => u.id === me),
        {
          name: a.name.trim().slice(0, 40) || "Игрок",
          bio: a.bio.slice(0, 300),
          country: a.country.slice(0, 40),
          color: a.color,
          status: a.status,
          initials: a.name.trim().slice(0, 2).toUpperCase(),
          avatar:
            typeof a.avatar === "string" &&
            /^data:image\/(png|jpeg|webp);base64,/.test(a.avatar) &&
            a.avatar.length < 750000
              ? a.avatar
              : "",
          cover: games.some((g) => g.id === a.cover) ? a.cover : "orbital",
        },
      );
      break;
    case "wishlist":
    case "cart": {
      need();
      if (!games.some((g) => g.id === a.game)) throw Error("Игра не найдена.");
      const x = list(a.type);
      n[a.type][me] = x.includes(a.game)
        ? x.filter((g) => g !== a.game)
        : [...x, a.game];
      break;
    }
    case "checkout": {
      need();
      const items = list("cart");
      if (!items.length) throw Error("Корзина пуста.");
      n.orders.unshift({
        id,
        user: me,
        games: [...items],
        total: items.reduce(
          (v, i) => v + price(games.find((g) => g.id === i)),
          0,
        ),
        at,
      });
      n.library[me] = [...new Set([...list("library"), ...items])];
      n.cart[me] = [];
      note("пополнил библиотеку");
      break;
    }
    case "request":
      need();
      if (a.user === me || !n.users.some((u) => u.id === a.user))
        throw Error("Выберите другого игрока.");
      if (friend(a.user)) throw Error("Заявка или дружба уже существует.");
      n.friends.push({ id, from: me, to: a.user, status: "pending" });
      break;
    case "accept": {
      need();
      const f = n.friends.find(
        (f) => f.id === a.friend && f.to === me && f.status === "pending",
      );
      if (!f) throw Error("Заявка недоступна.");
      f.status = "accepted";
      break;
    }
    case "unfriend": {
      need();
      const f = n.friends.find(
        (f) => f.id === a.friend && [f.from, f.to].includes(me),
      );
      if (!f) throw Error("Контакт недоступен.");
      if (f.status === "blocked" && f.blockedBy !== me)
        throw Error("Блокировку может снять её автор.");
      n.friends = n.friends.filter((x) => x !== f);
      break;
    }
    case "block": {
      need();
      const f = friend(a.user);
      if (!f || f.status === "blocked") throw Error("Контакт недоступен.");
      f.status = "blocked";
      f.blockedBy = me;
      break;
    }
    case "message":
      need();
      if (friend(a.user)?.status !== "accepted")
        throw Error("Переписка доступна только друзьям.");
      if (!a.text.trim() || a.text.length > 2000)
        throw Error("Сообщение: от 1 до 2000 символов.");
      n.messages.push({ id, from: me, to: a.user, text: a.text.trim(), at });
      break;
    case "topic":
      need();
      if (!a.title.trim() || !a.body.trim())
        throw Error("Заполните заголовок и текст.");
      n.topics.unshift({
        id,
        author: me,
        game: a.game,
        title: a.title.trim().slice(0, 120),
        body: a.body.slice(0, 5000),
        replies: [],
        at,
      });
      note("создал обсуждение");
      break;
    case "reply": {
      need();
      const t = n.topics.find((t) => t.id === a.topic);
      if (!t || !a.text.trim()) throw Error("Введите ответ.");
      t.replies.push({ id, author: me, text: a.text.slice(0, 2000), at });
      break;
    }
    case "edit-topic": {
      need();
      const t = n.topics.find((t) => t.id === a.topic && t.author === me);
      if (!t || !a.title.trim() || !a.body.trim())
        throw Error("Тема недоступна или не заполнена.");
      Object.assign(t, {
        title: a.title.trim().slice(0, 120),
        body: a.body.slice(0, 5000),
        game: a.game,
      });
      break;
    }
    case "edit-mod": {
      need();
      const m = n.mods.find((m) => m.id === a.mod && m.author === me);
      if (!m || !a.title.trim() || !a.description.trim())
        throw Error("Работа недоступна или не заполнена.");
      Object.assign(m, {
        title: a.title.slice(0, 100),
        description: a.description.slice(0, 2000),
        game: a.game,
        category: a.category,
        version: a.version.slice(0, 20),
        fileName: a.fileName || "",
      });
      break;
    }
    case "delete-mod":
      need();
      n.mods = n.mods.filter((m) => m.id !== a.mod || m.author !== me);
      for (const key of Object.keys(n.subscriptions)) {
        n.subscriptions[key] = n.subscriptions[key].filter((id) =>
          n.mods.some((m) => m.id === id),
        );
      }
      break;
    case "delete-topic":
      need();
      n.topics = n.topics.filter((t) => t.id !== a.topic || t.author !== me);
      break;
    case "mod":
      need();
      if (!a.title.trim() || !a.description.trim())
        throw Error("Заполните название и описание.");
      n.mods.unshift({
        id,
        author: me,
        title: a.title.slice(0, 100),
        description: a.description.slice(0, 2000),
        game: a.game,
        category: a.category,
        version: a.version.slice(0, 20) || "1.0",
        fileName: a.fileName || "",
        subscribers: 0,
      });
      note("добавил материал в мастерскую");
      break;
    case "subscribe": {
      need();
      const x = list("subscriptions");
      n.subscriptions[me] = x.includes(a.mod)
        ? x.filter((i) => i !== a.mod)
        : [...x, a.mod];
      break;
    }
    case "review":
      need();
      if (!list("library").includes(a.game))
        throw Error("Сначала добавьте игру в библиотеку.");
      if (!a.text.trim()) throw Error("Напишите отзыв.");
      n.reviews = n.reviews.filter(
        (r) => !(r.author === me && r.game === a.game),
      );
      n.reviews.unshift({
        id,
        author: me,
        game: a.game,
        text: a.text.slice(0, 2000),
        positive: a.positive,
        at,
      });
      break;
    case "settings":
      need();
      n.settings[me] = { ...n.settings[me], ...a.values };
      break;
    default:
      throw Error("Неизвестное действие.");
  }
  return n;
}
