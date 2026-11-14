
import React, { useEffect, useRef, useState } from "react";
import { ConfigProvider, message, Spin, Alert } from "antd";
import ruRU from "antd/locale/ru_RU";

import { Header } from "./components/Header";
import {
  Onboarding,
  type OnboardingAnswers,
} from "./components/Onboarding";
import {
  RecommendationsPage,
  type RecommendationGroup,
} from "./components/RecommendationsPage";

import {
  fetchDemoUsers,
  fetchBusinessGoals,
  fetchRecommendations,
  sendFeedback,
} from "./services/recommendationService";

import type {
  DemoUser,
  BusinessGoal,
  FeedbackType,
  RecommendationsRequest,
} from "./types";

type AppScreen = "onboarding" | "recommendations";

const App: React.FC = () => {
  // Пользователи и доступные бизнес-цели
  const [users, setUsers] = useState<DemoUser[]>([]);
  const [goals, setGoals] = useState<BusinessGoal[]>([]);
  const [selectedUserId, setSelectedUserId] = useState("");

  // Текущий экран
  const [screen, setScreen] = useState<AppScreen>("onboarding");

  // Сгруппированные рекомендации
  const [groups, setGroups] = useState<RecommendationGroup[]>([]);

  // Состояние загрузки
  const [initialLoading, setInitialLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Состояние обратной связи
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackMaterialId, setFeedbackMaterialId] = useState<
    string | null
  >(null);

  // Защита от устаревших ответов API
  const requestVersion = useRef(0);

  // Загружаем пользователей и цели
  useEffect(() => {
    let cancelled = false;

    const initialize = async () => {
      setInitialLoading(true);

      try {
        const [usersData, goalsData] = await Promise.all([
          fetchDemoUsers(),
          fetchBusinessGoals(),
        ]);

        if (cancelled) return;

        setUsers(usersData);
        setGoals(goalsData);

        if (usersData.length > 0) {
          setSelectedUserId(usersData[0].user_id);
        }
      } catch (err) {
        if (cancelled) return;

        console.error(err);
        setError("Не удалось загрузить данные приложения");
      } finally {
        if (!cancelled) {
          setInitialLoading(false);
        }
      }
    };

    void initialize();

    return () => {
      cancelled = true;
    };
  }, []);

  // При смене пользователя возвращаемся к опросу
  const handleUserChange = (userId: string) => {
    requestVersion.current += 1;

    setSelectedUserId(userId);
    setGroups([]);
    setError(null);
    setLoading(false);
    setScreen("onboarding");
  };

  // Формируем отдельную подборку для каждой цели
  const handleOnboardingSubmit = async (
    answers: OnboardingAnswers,
  ) => {
    if (!selectedUserId) {
      message.error("Пользователь не выбран");
      return;
    }

    const selectedGoals = goals.filter((goal) =>
      answers.goalIds.includes(goal.id),
    );

    const customGoal = answers.customGoal.trim();

    // Для собственной задачи используем существующий
    // goal_id как технический идентификатор.
    // Сам текст задачи передаётся в custom_goal.
    const fallbackGoalId =
      selectedGoals[0]?.id || goals[0]?.id;

    const requests: {
      goalId: string;
      goalTitle: string;
      request: RecommendationsRequest;
    }[] = selectedGoals.map((goal) => ({
      goalId: goal.id,
      goalTitle: goal.title,
      request: {
        user_id: selectedUserId,
        goal_id: goal.id,
        industry: answers.industry,
        business_stage: answers.businessStage,
        experience: answers.experience,
        preferred_formats: answers.preferredFormats,
      },
    }));

    if (customGoal && fallbackGoalId) {
      requests.push({
        goalId: "custom",
        goalTitle: customGoal,
        request: {
          user_id: selectedUserId,
          goal_id: fallbackGoalId,
          custom_goal: customGoal,
          industry: answers.industry,
          business_stage: answers.businessStage,
          experience: answers.experience,
          preferred_formats: answers.preferredFormats,
        },
      });
    }

    if (requests.length === 0) {
      message.warning("Выберите хотя бы одну бизнес-цель");
      return;
    }

    const currentVersion = ++requestVersion.current;

    setScreen("recommendations");
    setLoading(true);
    setError(null);
    setGroups([]);

    try {
      // Каждый запрос ранжируется независимо.
      const results = await Promise.all(
        requests.map(async (item) => {
          const route = await fetchRecommendations(item.request);

          return {
            goalId: item.goalId,
            goalTitle: item.goalTitle,
            route,
          } satisfies RecommendationGroup;
        }),
      );

      if (currentVersion !== requestVersion.current) {
        return;
      }

      setGroups(results);
    } catch (err) {
      if (currentVersion !== requestVersion.current) {
        return;
      }

      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Не удалось получить рекомендации",
      );
    } finally {
      if (currentVersion === requestVersion.current) {
        setLoading(false);
      }
    }
  };

  // Пересчёт отдельной подборки после обратной связи
  const handleFeedback = async (
    goalId: string,
    materialId: string,
    type: FeedbackType,
  ) => {
    if (feedbackLoading || loading) return;

    const currentGroup = groups.find(
      (group) => group.goalId === goalId,
    );

    if (!currentGroup) return;

    const currentVersion = requestVersion.current;

    setFeedbackLoading(true);
    setFeedbackMaterialId(materialId);

    try {
      const updatedRoute = await sendFeedback(
        {
          route_id: currentGroup.route.route_id,
          material_id: materialId,
          feedback_type: type,
        },
        currentGroup.route,
      );

      if (currentVersion !== requestVersion.current) {
        return;
      }

      // Обновляем только вкладку нужной бизнес-цели.
      setGroups((previousGroups) =>
        previousGroups.map((group) =>
          group.goalId === goalId
            ? {
                ...group,
                route: updatedRoute,
              }
            : group,
        ),
      );

      message.success("Подборка обновлена");
    } catch (err) {
      if (currentVersion !== requestVersion.current) {
        return;
      }

      console.error(err);
      message.error("Не удалось обработать обратную связь");
    } finally {
      if (currentVersion === requestVersion.current) {
        setFeedbackLoading(false);
        setFeedbackMaterialId(null);
      }
    }
  };

  // Возвращаемся к опросу
  const handleEditAnswers = () => {
    requestVersion.current += 1;

    setScreen("onboarding");
    setGroups([]);
    setError(null);
    setLoading(false);
    setFeedbackLoading(false);
    setFeedbackMaterialId(null);
  };

  return (
    <ConfigProvider
      locale={ruRU}
      theme={{
        token: {
          colorPrimary: "#EF3124",
          borderRadius: 8,
          fontFamily: "'Inter', sans-serif",
        },
      }}
    >
      <div style={styles.app}>
        <Header
          users={users}
          selectedUserId={selectedUserId}
          onUserChange={handleUserChange}
        />

        <main style={styles.main}>
          {initialLoading ? (
            <div style={styles.loadingContainer}>
              <Spin size="large" />
              <span>Загружаем Альфа-Путь...</span>
            </div>
          ) : error && screen === "onboarding" ? (
            <Alert
              type="error"
              showIcon
              message="Ошибка"
              description={error}
            />
          ) : screen === "onboarding" ? (
            <Onboarding
              goals={goals}
              onSubmit={handleOnboardingSubmit}
            />
          ) : (
            <RecommendationsPage
              groups={groups}
              loading={loading}
              error={error}
              feedbackLoading={feedbackLoading}
              feedbackMaterialId={feedbackMaterialId}
              onFeedback={handleFeedback}
              onEditAnswers={handleEditAnswers}
            />
          )}
        </main>

        <footer style={styles.footer}>
          Альфа-Путь · MVP для хакатона
          Changellenge Hack&Change 2026 · Трек 1
        </footer>
      </div>
    </ConfigProvider>
  );
};

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    background: "#F8FAFC",
  },

  main: {
    flex: 1,
    width: "100%",
    maxWidth: 1400,
    margin: "0 auto",
  },

  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 16,
    minHeight: 400,
    color: "#64748B",
  },

  footer: {
    padding: "16px 32px",
    textAlign: "center",
    fontSize: 12,
    color: "#9CA3AF",
    borderTop: "1px solid #E5E5E5",
    background: "#FFFFFF",
  },
};

export default App;
