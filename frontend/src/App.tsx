import React, { useState, useEffect } from "react";
import { ConfigProvider, message } from "antd";
import ruRU from "antd/locale/ru_RU";
import { Header } from "./components/Header";
import { GoalSelector } from "./components/GoalSelector";
import { Trajectory } from "./components/Trajectory";
import { UserProfile } from "./components/UserProfile";
import {
  fetchDemoUsers,
  fetchBusinessGoals,
  fetchRecommendations,
  sendFeedback,
} from "./services/recommendationService";
import type { DemoUser, BusinessGoal, Route, FeedbackType } from "./types";

const App: React.FC = () => {
  const [users, setUsers] = useState<DemoUser[]>([]);
  const [goals, setGoals] = useState<BusinessGoal[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [selectedGoalId, setSelectedGoalId] = useState<string>("");
  const [route, setRoute] = useState<Route | null>(null);
  const [loading, setLoading] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackMaterialId, setFeedbackMaterialId] = useState<string | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);

  // Загрузка пользователей и целей при монтировании
  useEffect(() => {
    const init = async () => {
      try {
        const [usersData, goalsData] = await Promise.all([
          fetchDemoUsers(),
          fetchBusinessGoals(),
        ]);
        setUsers(usersData);
        setGoals(goalsData);

        if (usersData.length > 0) {
          setSelectedUserId(usersData[0].user_id);
        }
        if (goalsData.length > 0) {
          setSelectedGoalId(goalsData[0].id);
        }
      } catch (err) {
        setError("Не удалось загрузить данные");
        console.error(err);
      }
    };
    init();
  }, []);

  // Загрузка рекомендаций при изменении пользователя или цели
  useEffect(() => {
    if (!selectedUserId || !selectedGoalId) return;

    const load = async () => {
      setLoading(true);
      setError(null);
      setRoute(null);
      setFeedbackMaterialId(null);

      try {
        const data = await fetchRecommendations({
          user_id: selectedUserId,
          goal_id: selectedGoalId,
        });
        setRoute(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Ошибка загрузки рекомендаций",
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [selectedUserId, selectedGoalId]);

  const handleUserChange = (userId: string) => {
    setSelectedUserId(userId);
    setFeedbackMaterialId(null);
  };

  const handleGoalChange = (goalId: string) => {
    setSelectedGoalId(goalId);
    setFeedbackMaterialId(null);
  };

  const handleFeedback = async (materialId: string, type: FeedbackType) => {
    if (!route) return;

    setFeedbackMaterialId(materialId);
    setFeedbackLoading(true);

    const feedbackLabels: Record<FeedbackType, string> = {
      already_know: "Уже знаю",
      too_hard: "Слишком сложно",
      irrelevant: "Неактуально",
    };

    try {
      const updatedRoute = await sendFeedback(
        {
          route_id: route.route_id,
          material_id: materialId,
          feedback_type: type,
        },
        route,
      );
      setRoute(updatedRoute);
      message.success(
        `Обратная связь «${feedbackLabels[type]}» учтена. Маршрут пересчитан.`,
      );
    } catch (err) {
      message.error("Не удалось обработать обратную связь");
      console.error(err);
    } finally {
      setFeedbackLoading(false);
      setFeedbackMaterialId(null);
    }
  };

  const currentUser = users.find((u) => u.user_id === selectedUserId) || null;

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
          <div style={styles.content}>
            <GoalSelector
              goals={goals}
              selectedGoalId={selectedGoalId}
              onGoalChange={handleGoalChange}
            />

            <Trajectory
              route={route}
              loading={loading}
              error={error}
              feedbackMaterialId={feedbackMaterialId}
              onFeedback={handleFeedback}
              feedbackLoading={feedbackLoading}
            />
          </div>

          <aside style={styles.sidebar}>
            <UserProfile user={currentUser} />
          </aside>
        </main>

        <footer style={styles.footer}>
          Альфа-Путь · MVP для хакатона Changellenge Hack&Change 2026 · Трек 1
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
  },
  main: {
    flex: 1,
    display: "grid",
    gridTemplateColumns: "1fr 320px",
    gap: 24,
    padding: "24px 32px",
    maxWidth: 1400,
    width: "100%",
    margin: "0 auto",
  },
  content: {
    minWidth: 0,
  },
  sidebar: {
    minWidth: 0,
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
