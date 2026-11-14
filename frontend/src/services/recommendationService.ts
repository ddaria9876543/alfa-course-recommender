
import type {
  DemoUser,
  BusinessGoal,
  Material,
  MaterialType,
  Route,
  Recommendation,
  RecommendationsRequest,
  FeedbackRequest,
} from "../types";

import {
  demoUsers,
  businessGoals,
  stepLabels,
} from "../mock/data";

const API_URL = "http://127.0.0.1:8001/api";

interface ApiRecommendation {
  material_id: string;
  title: string;
  material_type: string;
  url: string | null;
  score: number;
  reason_factors: string[];
  explanation: string;
  step: number;
}

interface ApiRoute {
  route_id: string;
  user_id: number;
  goal: string;
  recommendations: ApiRecommendation[];
}

interface ApiMaterial {
  description?: string | null;
  topics?: string | string[] | null;
  tags?: string | string[] | null;
  url?: string | null;
}

async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        detail = error.detail;
      }
    } catch {
      // Оставляем стандартное описание HTTP-ошибки.
    }

    throw new Error(
      `Ошибка API ${response.status}: ${detail}`,
    );
  }

  return response.json() as Promise<T>;
}

function parseValues(
  value: string | string[] | null | undefined,
): string[] {
  if (Array.isArray(value)) return value;
  if (!value) return [];

  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function getValidUrl(
  value: string | null | undefined,
): string {
  if (!value) return "";

  try {
    const url = new URL(value);

    return ["https:", "http:"].includes(url.protocol)
      ? url.href
      : "";
  } catch {
    return "";
  }
}

// Получаем дополнительные сведения о материале.
async function fetchMaterial(
  id: string,
): Promise<ApiMaterial | null> {
  try {
    return await apiRequest<ApiMaterial>(
      `/materials/${encodeURIComponent(id)}`,
    );
  } catch (error) {
    console.warn(
      `Не удалось загрузить материал ${id}`,
      error,
    );

    return null;
  }
}

// Преобразуем ответ Backend в формат React.
// Теперь сохраняем все рекомендации, а не только Top-3.
async function convertApiRoute(
  result: ApiRoute,
  frontendUserId: string,
  goal: BusinessGoal,
): Promise<Route> {
  const recommendations: Recommendation[] =
    await Promise.all(
      result.recommendations.map(
        async (item, index) => {
          const details = await fetchMaterial(
            item.material_id,
          );

          const materialType: MaterialType =
            item.material_type === "course" ||
            item.material_type === "document"
              ? item.material_type
              : "article";

          const material: Material = {
            material_id: item.material_id,
            material_type: materialType,
            title: item.title,
            description: details?.description || "",
            topics: parseValues(details?.topics),
            tags: parseValues(details?.tags),
            url: getValidUrl(
              details?.url || item.url,
            ),
          };

          // Старые компоненты ещё используют step.
          // Ограничиваем значение для совместимости.
          // В новом RecommendationsPage шаги не выводятся.
          const legacyStep = Math.min(
            index + 1,
            3,
          ) as 1 | 2 | 3;

          return {
            material,
            step: legacyStep,
            step_label: stepLabels[legacyStep],
            score: item.score,
            reason_factors: item.reason_factors,
            explanation: item.explanation,
          };
        },
      ),
    );

  return {
    route_id: result.route_id,
    user_id: frontendUserId,
    goal,
    recommendations,
    created_at: new Date().toISOString(),
  };
}

export async function fetchDemoUsers(): Promise<
  DemoUser[]
> {
  return demoUsers;
}

export async function fetchBusinessGoals(): Promise<
  BusinessGoal[]
> {
  return businessGoals;
}

// Запрашиваем рекомендации по одной бизнес-цели.
// App.tsx вызывает эту функцию отдельно для каждой цели.
export async function fetchRecommendations(
  request: RecommendationsRequest,
): Promise<Route> {
  const selectedGoal = businessGoals.find(
    (item) => item.id === request.goal_id,
  );

  if (!selectedGoal) {
    throw new Error("Бизнес-цель не найдена");
  }

  const customGoal =
    request.custom_goal?.trim() || "";

  const goal: BusinessGoal = customGoal
    ? {
        ...selectedGoal,
        id: "custom",
        title: customGoal,
      }
    : selectedGoal;

  const userIndex = demoUsers.findIndex(
    (user) =>
      user.user_id === request.user_id,
  );

  if (userIndex === -1) {
    throw new Error("Пользователь не найден");
  }

  // Временное сопоставление демонстрационных
  // пользователей Frontend и Backend.
  const backendUserId = userIndex + 1;

  const result = await apiRequest<ApiRoute>(
    "/recommendations",
    {
      method: "POST",
      body: JSON.stringify({
      user_id: backendUserId,
      goal: goal.title,
      industry: request.industry || null,
      preferred_format: request.preferred_format || null,
      preferred_formats: request.preferred_formats ?? null,
      business_stage: request.business_stage || null,
      experience: request.experience || null,
      }),
    },
  );

  return convertApiRoute(
    result,
    request.user_id,
    goal,
  );
}

// Сохраняем обратную связь и получаем
// обновлённую подборку той же бизнес-цели.
export async function sendFeedback(
  request: FeedbackRequest,
  currentRoute: Route,
): Promise<Route> {
  const updatedRoute = await apiRequest<ApiRoute>(
    "/recommendations/feedback",
    {
      method: "POST",
      body: JSON.stringify(request),
    },
  );

  return convertApiRoute(
    updatedRoute,
    currentRoute.user_id,
    currentRoute.goal,
  );
}
