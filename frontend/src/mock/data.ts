import type { DemoUser, BusinessGoal, Material, Route } from "../types";

export const demoUsers: DemoUser[] = [
  {
    user_id: "user-new",
    name: "Новый предприниматель",
    avatar_initials: "НП",
    has_history: false,
    interests: [],
    level: "beginner",
    completed_materials: [],
    history_summary:
      "История обучения отсутствует. Рекомендации строятся на основе выбранной бизнес-цели.",
  },
  {
    user_id: "user-experienced",
    name: "Опытный предприниматель",
    avatar_initials: "ОП",
    has_history: true,
    interests: ["маркетинг", "продажи", "аналитика"],
    level: "intermediate",
    completed_materials: ["mat-001", "mat-003"],
    history_summary:
      "Изучено 2 материала по маркетингу. Пройден вводный курс по продажам.",
  },
];

export const businessGoals: BusinessGoal[] = [
  {
    id: "goal-sales",
    title: "Увеличить продажи",
    description: "Найти способы роста выручки и конверсии",
  },
  {
    id: "goal-start",
    title: "Запустить собственный бизнес",
    description: "Разобраться с первыми шагами и регистрацией",
  },
  {
    id: "goal-finance",
    title: "Разобраться с финансами",
    description: "Наладить учёт, налоги и управление деньгами",
  },
  {
    id: "goal-marketing",
    title: "Улучшить маркетинг и продвижение",
    description: "Привлечь клиентов и повысить узнаваемость",
  },
];

export const materials: Material[] = [
  {
    material_id: "mat-001",
    material_type: "article",
    title: "Основы воронки продаж для малого бизнеса",
    description:
      "Разбираем, как построить простую воронку продаж и увеличить конверсию на каждом этапе.",
    topics: ["продажи", "воронка"],
    tags: ["продажи", "конверсия", "воронка"],
    url: "https://alfabank.ru/education/business/sales/",
    difficulty: "beginner",
  },
  {
    material_id: "mat-002",
    material_type: "course",
    title: "Курс: Маркетинг с нуля до первых клиентов",
    description:
      "Пошаговый курс по запуску маркетинга: от исследования аудитории до первых рекламных кампаний.",
    topics: ["маркетинг", "реклама"],
    tags: ["маркетинг", "реклама", "аудитория"],
    url: "https://alfabank.ru/education/business/marketing/",
    difficulty: "beginner",
  },
  {
    material_id: "mat-003",
    material_type: "document",
    title: "Чек-лист: запуск бизнеса за 30 дней",
    description:
      "Практический чек-лист с основными шагами регистрации и запуска бизнеса.",
    topics: ["запуск бизнеса", "регистрация"],
    tags: ["запуск", "регистрация", "чек-лист"],
    url: "https://alfabank.ru/education/business/start/",
    difficulty: "beginner",
  },
  {
    material_id: "mat-004",
    material_type: "article",
    title: "Как считать unit-экономику и не разориться",
    description:
      "Разбираем ключевые метрики: LTV, CAC, маржинальность. Примеры расчётов для малого бизнеса.",
    topics: ["финансы", "аналитика"],
    tags: ["финансы", "unit-экономика", "метрики"],
    url: "https://alfabank.ru/education/business/finance/",
    difficulty: "intermediate",
  },
  {
    material_id: "mat-005",
    material_type: "course",
    title: "Курс: Продвинутый digital-маркетинг",
    description:
      "Глубокое погружение в performance-маркетинг, SEO и аналитику рекламных каналов.",
    topics: ["маркетинг", "аналитика"],
    tags: ["маркетинг", "digital", "аналитика", "SEO"],
    url: "https://alfabank.ru/education/business/digital-marketing/",
    difficulty: "advanced",
  },
  {
    material_id: "mat-006",
    material_type: "article",
    title: "Налоги для ИП на УСН: что нужно знать",
    description:
      "Краткий гид по налогообложению для индивидуальных предпринимателей на упрощёнке.",
    topics: ["финансы", "налоги"],
    tags: ["налоги", "ИП", "УСН"],
    url: "https://alfabank.ru/education/business/taxes/",
    difficulty: "beginner",
  },
  {
    material_id: "mat-007",
    material_type: "document",
    title: "Шаблон бизнес-плана для стартапа",
    description:
      "Готовый шаблон бизнес-плана с пояснениями по каждому разделу.",
    topics: ["запуск бизнеса", "планирование"],
    tags: ["бизнес-план", "шаблон", "стартап"],
    url: "https://alfabank.ru/education/business/business-plan/",
    difficulty: "beginner",
  },
  {
    material_id: "mat-008",
    material_type: "article",
    title: "A/B-тесты: как проверять гипотезы без бюджета",
    description:
      "Практические методы проверки маркетинговых гипотез при ограниченных ресурсах.",
    topics: ["маркетинг", "аналитика"],
    tags: ["A/B-тесты", "гипотезы", "маркетинг"],
    url: "https://alfabank.ru/education/business/ab-testing/",
    difficulty: "intermediate",
  },
  {
    material_id: "mat-009",
    material_type: "course",
    title: "Курс: Финансовый учёт для предпринимателей",
    description:
      "Системный курс по ведению финансового учёта, планированию и отчётности.",
    topics: ["финансы", "учёт"],
    tags: ["финансы", "учёт", "отчётность"],
    url: "https://alfabank.ru/education/business/accounting/",
    difficulty: "intermediate",
  },
  {
    material_id: "mat-010",
    material_type: "article",
    title: "Как работать с возражениями клиентов",
    description:
      "Разбор типичных возражений и проверенные скрипты для их обработки.",
    topics: ["продажи", "коммуникация"],
    tags: ["продажи", "возражения", "скрипты"],
    url: "https://alfabank.ru/education/business/objections/",
    difficulty: "intermediate",
  },
];

export const materialTypeLabels: Record<string, string> = {
  article: "Статья",
  course: "Курс",
  document: "Документ",
};

export const stepLabels: Record<number, string> = {
  1: "Следующий шаг",
  2: "Практическое продолжение",
  3: "Углубление темы",
};

export const mockRoutes: Record<string, Record<string, Route>> = {
  "user-new": {
    "goal-sales": {
      route_id: "route-new-sales",
      user_id: "user-new",
      goal: businessGoals[0],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[0],
          step: 1,
          step_label: stepLabels[1],
          score: 0.92,
          reason_factors: [
            "соответствие бизнес-цели",
            "подходящий уровень",
            "популярно среди новичков",
          ],
          explanation:
            "Этот материал поможет понять основы воронки продаж — с чего стоит начать, чтобы увеличить выручку.",
        },
        {
          material: materials[9],
          step: 2,
          step_label: stepLabels[2],
          score: 0.78,
          reason_factors: ["логичное продолжение", "практическое применение"],
          explanation:
            "После изучения воронки полезно научиться работать с возражениями — это повысит конверсию на финальном этапе.",
        },
        {
          material: materials[1],
          step: 3,
          step_label: stepLabels[3],
          score: 0.71,
          reason_factors: ["системное обучение", "углубление темы"],
          explanation:
            "Если хотите глубоко разобраться в привлечении клиентов, этот курс даст полную картину маркетинга.",
        },
      ],
    },
    "goal-start": {
      route_id: "route-new-start",
      user_id: "user-new",
      goal: businessGoals[1],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[2],
          step: 1,
          step_label: stepLabels[1],
          score: 0.95,
          reason_factors: ["точное соответствие цели", "практический формат"],
          explanation:
            "Чек-лист поможет не упустить важные шаги при запуске бизнеса — начните с него.",
        },
        {
          material: materials[6],
          step: 2,
          step_label: stepLabels[2],
          score: 0.88,
          reason_factors: [
            "документ для применения",
            "структурирует планирование",
          ],
          explanation:
            "Шаблон бизнес-плана поможет оформить идею и проверить её жизнеспособность.",
        },
        {
          material: materials[5],
          step: 3,
          step_label: stepLabels[3],
          score: 0.74,
          reason_factors: ["юридические основы", "важно для ИП"],
          explanation:
            "Разобраться с налогами лучше на старте — это сэкономит время и деньги в будущем.",
        },
      ],
    },
    "goal-finance": {
      route_id: "route-new-finance",
      user_id: "user-new",
      goal: businessGoals[2],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[5],
          step: 1,
          step_label: stepLabels[1],
          score: 0.93,
          reason_factors: ["базовый уровень", "соответствие цели"],
          explanation:
            "Начните с налогового ликбеза — это основа финансового грамотного предпринимателя.",
        },
        {
          material: materials[3],
          step: 2,
          step_label: stepLabels[2],
          score: 0.85,
          reason_factors: ["ключевые метрики", "практическая ценность"],
          explanation:
            "Unit-экономика поможет понять, действительно ли ваш бизнес зарабатывает.",
        },
        {
          material: materials[8],
          step: 3,
          step_label: stepLabels[3],
          score: 0.76,
          reason_factors: ["системный подход", "углубление"],
          explanation:
            "Для полноценного учёта и планирования подойдёт этот курс по финансовому учёту.",
        },
      ],
    },
    "goal-marketing": {
      route_id: "route-new-marketing",
      user_id: "user-new",
      goal: businessGoals[3],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[1],
          step: 1,
          step_label: stepLabels[1],
          score: 0.94,
          reason_factors: ["вводный материал", "соответствие цели"],
          explanation:
            "Курс даст базовое понимание маркетинга — с него стоит начать, если опыта мало.",
        },
        {
          material: materials[7],
          step: 2,
          step_label: stepLabels[2],
          score: 0.81,
          reason_factors: ["практический инструмент", "без бюджета"],
          explanation:
            "A/B-тесты помогут проверять гипотезы даже при ограниченном рекламном бюджете.",
        },
        {
          material: materials[4],
          step: 3,
          step_label: stepLabels[3],
          score: 0.73,
          reason_factors: ["углублённое изучение", "performance-маркетинг"],
          explanation:
            "Для системного роста нужен продвинутый digital-маркетинг — этот курс закроет тему.",
        },
      ],
    },
  },
  "user-experienced": {
    "goal-sales": {
      route_id: "route-exp-sales",
      user_id: "user-experienced",
      goal: businessGoals[0],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[9],
          step: 1,
          step_label: stepLabels[1],
          score: 0.91,
          reason_factors: [
            "учтён предыдущий опыт",
            "пропущены основы",
            "практическая ценность",
          ],
          explanation:
            "Вы уже знакомы с основами воронки — сразу переходим к работе с возражениями, это даст быстрый результат.",
        },
        {
          material: materials[3],
          step: 2,
          step_label: stepLabels[2],
          score: 0.83,
          reason_factors: ["аналитический подход", "соответствует уровню"],
          explanation:
            "Unit-экономика поможет оценить эффективность продаж в цифрах и найти точки роста.",
        },
        {
          material: materials[4],
          step: 3,
          step_label: stepLabels[3],
          score: 0.75,
          reason_factors: ["углубление", "связь с аналитикой"],
          explanation:
            "Продвинутый маркетинг дополнит картину и поможет масштабировать продажи через новые каналы.",
        },
      ],
    },
    "goal-start": {
      route_id: "route-exp-start",
      user_id: "user-experienced",
      goal: businessGoals[1],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[5],
          step: 1,
          step_label: stepLabels[1],
          score: 0.89,
          reason_factors: [
            "учтён уровень пользователя",
            "пропущены базовые чек-листы",
          ],
          explanation:
            "Учитывая ваш опыт, сразу переходим к налогам — это то, что чаще всего упускают при запуске.",
        },
        {
          material: materials[3],
          step: 2,
          step_label: stepLabels[2],
          score: 0.82,
          reason_factors: ["финансовая основа", "практическая ценность"],
          explanation:
            "Unit-экономика поможет сразу оценить жизнеспособность бизнес-идеи в цифрах.",
        },
        {
          material: materials[7],
          step: 3,
          step_label: stepLabels[3],
          score: 0.74,
          reason_factors: ["маркетинг с аналитикой", "соответствует интересам"],
          explanation:
            "A/B-тесты помогут проверять гипотезы по продукту и маркетингу без больших затрат.",
        },
      ],
    },
    "goal-finance": {
      route_id: "route-exp-finance",
      user_id: "user-experienced",
      goal: businessGoals[2],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[3],
          step: 1,
          step_label: stepLabels[1],
          score: 0.92,
          reason_factors: ["соответствие уровню", "ключевые метрики"],
          explanation:
            "Вы готовы к цифрам — unit-экономика станет основой для принятия финансовых решений.",
        },
        {
          material: materials[7],
          step: 2,
          step_label: stepLabels[2],
          score: 0.84,
          reason_factors: ["аналитика", "связано с интересами"],
          explanation:
            "A/B-тесты помогут проверять финансовые и маркетинговые гипотезы на практике.",
        },
        {
          material: materials[8],
          step: 3,
          step_label: stepLabels[3],
          score: 0.77,
          reason_factors: ["системный учёт", "углубление"],
          explanation:
            "Курс по финансовому учёту закроет тему системного управления деньгами бизнеса.",
        },
      ],
    },
    "goal-marketing": {
      route_id: "route-exp-marketing",
      user_id: "user-experienced",
      goal: businessGoals[3],
      created_at: new Date().toISOString(),
      recommendations: [
        {
          material: materials[7],
          step: 1,
          step_label: stepLabels[1],
          score: 0.9,
          reason_factors: ["учтён опыт", "пропущен вводный курс", "практика"],
          explanation:
            "Вместо базового курса сразу переходим к A/B-тестам — это даст быстрый практический результат.",
        },
        {
          material: materials[3],
          step: 2,
          step_label: stepLabels[2],
          score: 0.82,
          reason_factors: ["аналитика маркетинга", "связано с интересами"],
          explanation:
            "Unit-экономика поможет оценить эффективность маркетинговых каналов в деньгах.",
        },
        {
          material: materials[4],
          step: 3,
          step_label: stepLabels[3],
          score: 0.76,
          reason_factors: ["углубление", "performance-маркетинг"],
          explanation:
            "Продвинутый digital-маркетинг систематизирует знания и откроет новые каналы роста.",
        },
      ],
    },
  },
};

export const mockRoutesAfterFeedback: Record<string, Route> = {
  already_know: {
    route_id: "route-feedback-ak",
    user_id: "",
    goal: businessGoals[0],
    created_at: new Date().toISOString(),
    recommendations: [
      {
        material: materials[3],
        step: 1,
        step_label: stepLabels[1],
        score: 0.88,
        reason_factors: [
          "пользователь отметил «Уже знаю»",
          "повышен уровень сложности",
        ],
        explanation:
          "Раз основы уже знакомы, переходим к unit-экономике — это следующий логичный шаг.",
      },
      {
        material: materials[7],
        step: 2,
        step_label: stepLabels[2],
        score: 0.81,
        reason_factors: ["практическое применение", "аналитика"],
        explanation:
          "A/B-тесты помогут применять знания на практике и проверять гипотезы.",
      },
      {
        material: materials[4],
        step: 3,
        step_label: stepLabels[3],
        score: 0.75,
        reason_factors: ["углубление", "системный подход"],
        explanation:
          "Продвинутый курс закрепит результат и даст инструменты для масштабирования.",
      },
    ],
  },
  too_hard: {
    route_id: "route-feedback-th",
    user_id: "",
    goal: businessGoals[0],
    created_at: new Date().toISOString(),
    recommendations: [
      {
        material: materials[0],
        step: 1,
        step_label: stepLabels[1],
        score: 0.9,
        reason_factors: [
          "пользователь отметил «Слишком сложно»",
          "понижен уровень",
        ],
        explanation:
          "Подобрали более доступный материал — он объяснит основы простым языком.",
      },
      {
        material: materials[2],
        step: 2,
        step_label: stepLabels[2],
        score: 0.83,
        reason_factors: ["практический формат", "низкий порог входа"],
        explanation:
          "Чек-лист поможет закрепить материал в формате пошаговой инструкции.",
      },
      {
        material: materials[5],
        step: 3,
        step_label: stepLabels[3],
        score: 0.74,
        reason_factors: ["базовый уровень", "важная тема"],
        explanation:
          "Налоги — важная тема, которую стоит изучить в комфортном темпе.",
      },
    ],
  },
  irrelevant: {
    route_id: "route-feedback-ir",
    user_id: "",
    goal: businessGoals[0],
    created_at: new Date().toISOString(),
    recommendations: [
      {
        material: materials[1],
        step: 1,
        step_label: stepLabels[1],
        score: 0.87,
        reason_factors: [
          "исключён неактуальный материал",
          "альтернативное направление",
        ],
        explanation:
          "Учли обратную связь и подобрали материал из смежной, но более релевантной области.",
      },
      {
        material: materials[8],
        step: 2,
        step_label: stepLabels[2],
        score: 0.8,
        reason_factors: ["практика", "новый ракурс"],
        explanation:
          "Финансовый учёт даст другую перспективу и поможет увидеть новые возможности.",
      },
      {
        material: materials[9],
        step: 3,
        step_label: stepLabels[3],
        score: 0.72,
        reason_factors: ["углубление", "смежная тема"],
        explanation:
          "Работа с возражениями дополнит картину и повысит конверсию в продажах.",
      },
    ],
  },
};
