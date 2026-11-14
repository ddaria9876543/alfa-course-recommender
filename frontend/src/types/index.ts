
export type MaterialType = "article" | "course" | "document";

export type FeedbackType =
  | "already_know"
  | "too_hard"
  | "irrelevant";

export type BusinessStage = "planning" | "running";

export type ExperienceLevel = "beginner" | "experienced";

export type PreferredFormat = MaterialType;

// Бизнес-цель
export interface BusinessGoal {
  id: string;
  title: string;
  description: string;
}

// Образовательный материал
export interface Material {
  material_id: string;
  material_type: MaterialType;
  title: string;
  description: string;
  topics: string[];
  tags: string[];
  url: string;
  difficulty?: "beginner" | "intermediate" | "advanced";
}

// Рекомендация ML-модели
export interface Recommendation {
  material: Material;

  // Временные поля для совместимости
  // с текущим Backend и существующими компонентами.
  step: 1 | 2 | 3;
  step_label: string;

  // Внутренняя оценка модели.
  // Не является вероятностью полезности материала.
  score: number;

  reason_factors: string[];
  explanation: string;
}

// Подборка по одной бизнес-цели
export interface Route {
  route_id: string;
  user_id: string;
  goal: BusinessGoal;
  recommendations: Recommendation[];
  created_at: string;
}

// Демонстрационный пользователь
export interface DemoUser {
  user_id: string;
  name: string;
  avatar_initials: string;
  has_history: boolean;
  interests: string[];
  level: "beginner" | "intermediate" | "advanced";
  completed_materials: string[];
  history_summary: string;
}

// Запрос рекомендаций.
// Пока один запрос соответствует одной бизнес-цели.
export interface RecommendationsRequest {
  user_id: string;
  goal_id: string;
  custom_goal?: string;
  industry?: string;

  // Старый параметр для совместимости
  preferred_format?: string;

  // Новый параметр для нескольких форматов
  preferred_formats?: ("article" | "course" | "document")[];

  business_stage?: "planning" | "running";
  experience?: "beginner" | "experienced";
}

// Обратная связь по материалу
export interface FeedbackRequest {
  route_id: string;
  material_id: string;
  feedback_type: FeedbackType;
}
