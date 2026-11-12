export type MaterialType = "article" | "course" | "document";
export type FeedbackType = "already_know" | "too_hard" | "irrelevant";

export interface BusinessGoal {
  id: string;
  title: string;
  description: string;
}

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

export interface Recommendation {
  material: Material;
  step: 1 | 2 | 3;
  step_label: string;
  score: number;
  reason_factors: string[];
  explanation: string;
}

export interface Route {
  route_id: string;
  user_id: string;
  goal: BusinessGoal;
  recommendations: Recommendation[];
  created_at: string;
}

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

export interface RecommendationsRequest {
  user_id: string;
  goal_id: string;
}

export interface FeedbackRequest {
  route_id: string;
  material_id: string;
  feedback_type: FeedbackType;
}
