import type {
  DemoUser,
  BusinessGoal,
  Route,
  RecommendationsRequest,
  FeedbackRequest,
} from "../types";
import {
  demoUsers,
  businessGoals,
  mockRoutes,
  mockRoutesAfterFeedback,
} from "../mock/data";

export async function fetchDemoUsers(): Promise<DemoUser[]> {
  await delay(300);
  return demoUsers;
}

export async function fetchBusinessGoals(): Promise<BusinessGoal[]> {
  await delay(200);
  return businessGoals;
}

export async function fetchRecommendations(
  request: RecommendationsRequest,
): Promise<Route> {
  await delay(500);
  const userRoutes = mockRoutes[request.user_id];
  if (!userRoutes) throw new Error(`Пользователь ${request.user_id} не найден`);
  const route = userRoutes[request.goal_id];
  if (!route) throw new Error(`Маршрут для цели ${request.goal_id} не найден`);
  return route;
}

export async function sendFeedback(
  request: FeedbackRequest,
  currentRoute: Route,
): Promise<Route> {
  await delay(600);
  const updatedRoute = mockRoutesAfterFeedback[request.feedback_type];
  if (!updatedRoute)
    throw new Error(`Неизвестный тип обратной связи: ${request.feedback_type}`);
  return {
    ...updatedRoute,
    user_id: currentRoute.user_id,
    goal: currentRoute.goal,
  };
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
