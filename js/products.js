/*
 * Каталог на производи за MARELI (примерни податоци).
 * За да додадете нов производ, копирајте еден објект и изменете ги полињата.
 * Полето "tags" се користи за филтрирање на страницата.
 * "type" одредува кој илустративен приказ се користи: "rim" или "tire".
 */
const PRODUCTS = [
  /* ----------------------------- ФЕЛНИ ----------------------------- */
  {
    id: "rim-001",
    category: "rims",
    type: "rim",
    name: "Mareli Sport R18",
    brand: "Mareli",
    price: "од 6.900 ден.",
    desc: "Лесна алуминиумска фелна со 5 краци, идеална за спортски возила.",
    tags: ["Алуминиумски", "18 цоли", "5 краци", "Сребрена"]
  },
  {
    id: "rim-002",
    category: "rims",
    type: "rim",
    name: "Mareli Black Edition R19",
    brand: "Mareli",
    price: "од 8.500 ден.",
    desc: "Матно црна фелна со агресивен дизајн за SUV возила.",
    tags: ["Алуминиумски", "19 цоли", "Мулти-крак", "Црна"]
  },
  {
    id: "rim-003",
    category: "rims",
    type: "rim",
    name: "Mareli Classic R16",
    brand: "Mareli",
    price: "од 4.200 ден.",
    desc: "Класична челична фелна, отпорна и економична.",
    tags: ["Челични", "16 цоли", "Сребрена"]
  },
  {
    id: "rim-004",
    category: "rims",
    type: "rim",
    name: "Mareli Luxe R20",
    brand: "Mareli",
    price: "од 11.900 ден.",
    desc: "Премиум фелна со полиран двобоен финиш за луксузни возила.",
    tags: ["Алуминиумски", "20 цоли", "Двобојна", "Полирана"]
  },
  {
    id: "rim-005",
    category: "rims",
    type: "rim",
    name: "Mareli Urban R17",
    brand: "Mareli",
    price: "од 5.400 ден.",
    desc: "Универзална фелна за градско возење со 10 краци.",
    tags: ["Алуминиумски", "17 цоли", "10 краци", "Сива"]
  },
  {
    id: "rim-006",
    category: "rims",
    type: "rim",
    name: "Mareli Offroad R18",
    brand: "Mareli",
    price: "од 9.300 ден.",
    desc: "Зајакната фелна за теренски и 4x4 возила.",
    tags: ["Алуминиумски", "18 цоли", "Off-road", "Црна"]
  },
  {
    id: "rim-007",
    category: "rims",
    type: "rim",
    name: "Mareli Eco R15",
    brand: "Mareli",
    price: "од 3.600 ден.",
    desc: "Економична челична фелна за помали возила.",
    tags: ["Челични", "15 цоли", "Сребрена"]
  },
  {
    id: "rim-008",
    category: "rims",
    type: "rim",
    name: "Mareli GT R19",
    brand: "Mareli",
    price: "од 9.900 ден.",
    desc: "Аеродинамичен дизајн со 5 двојни краци за перформанси.",
    tags: ["Алуминиумски", "19 цоли", "5 краци", "Бронзена"]
  },

  /* ----------------------------- ГУМИ ----------------------------- */
  {
    id: "tire-001",
    category: "tires",
    type: "tire",
    name: "Mareli Summer Pro 205/55 R16",
    brand: "Mareli",
    price: "од 2.800 ден.",
    desc: "Летна гума со одличен грип на суво и мокро.",
    tags: ["Летни", "16 цоли", "205/55", "Патнички"]
  },
  {
    id: "tire-002",
    category: "tires",
    type: "tire",
    name: "Mareli Winter Grip 225/45 R17",
    brand: "Mareli",
    price: "од 3.500 ден.",
    desc: "Зимска гума со длабока шара за снег и мраз.",
    tags: ["Зимски", "17 цоли", "225/45", "Патнички"]
  },
  {
    id: "tire-003",
    category: "tires",
    type: "tire",
    name: "Mareli AllSeason 195/65 R15",
    brand: "Mareli",
    price: "од 3.100 ден.",
    desc: "Целогодишна гума погодна за сите временски услови.",
    tags: ["Целогодишни", "15 цоли", "195/65", "Патнички"]
  },
  {
    id: "tire-004",
    category: "tires",
    type: "tire",
    name: "Mareli SUV Terrain 265/65 R18",
    brand: "Mareli",
    price: "од 5.900 ден.",
    desc: "Издржлива гума за SUV и теренски возила.",
    tags: ["Летни", "18 цоли", "265/65", "SUV"]
  },
  {
    id: "tire-005",
    category: "tires",
    type: "tire",
    name: "Mareli Winter SUV 235/60 R18",
    brand: "Mareli",
    price: "од 6.200 ден.",
    desc: "Зимска гума за SUV со сигурно сопирање на снег.",
    tags: ["Зимски", "18 цоли", "235/60", "SUV"]
  },
  {
    id: "tire-006",
    category: "tires",
    type: "tire",
    name: "Mareli Sport Max 245/40 R19",
    brand: "Mareli",
    price: "од 5.400 ден.",
    desc: "Спортска гума за високи перформанси и брзина.",
    tags: ["Летни", "19 цоли", "245/40", "Спортски"]
  },
  {
    id: "tire-007",
    category: "tires",
    type: "tire",
    name: "Mareli City 175/70 R14",
    brand: "Mareli",
    price: "од 2.300 ден.",
    desc: "Економична летна гума за градско возење.",
    tags: ["Летни", "14 цоли", "175/70", "Патнички"]
  },
  {
    id: "tire-008",
    category: "tires",
    type: "tire",
    name: "Mareli Winter City 185/65 R15",
    brand: "Mareli",
    price: "од 2.900 ден.",
    desc: "Зимска гума за помали градски возила.",
    tags: ["Зимски", "15 цоли", "185/65", "Патнички"]
  }
];
