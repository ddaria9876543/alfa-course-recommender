import React from "react";
import { Spin, Empty, Alert } from "antd";
import type { Route, FeedbackType } from "../types";
import { MaterialCard } from "./MaterialCard";

interface TrajectoryProps {
  route: Route | null;
  loading: boolean;
  error: string | null;
  feedbackLoading: boolean;
  onFeedback: (materialId: string, type: FeedbackType) => void;
  feedbackMaterialId?: string | null;
}

export const Trajectory: React.FC<TrajectoryProps> = ({
  route,
  loading,
  error,
  feedbackLoading,
  onFeedback,
  feedbackMaterialId,
}) => {
  if (loading) {
    return (
      <div style={styles.centered}>
        <Spin size="large" />
        <div style={styles.loadingText}>
          Подбираем персональную траекторию...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Ошибка загрузки рекомендаций"
        description={error}
        type="error"
        showIcon
        style={{ borderRadius: 12 }}
      />
    );
  }

  if (!route || route.recommendations.length === 0) {
    return (
      <Empty
        description="Рекомендации не найдены. Попробуйте другую бизнес-цель."
        style={{ padding: 40 }}
      />
    );
  }

  const [primary, ...secondary] = route.recommendations;

  return (
    <div>
      <div style={styles.sectionTitle}>Ваша образовательная траектория</div>

      {primary && (
        <MaterialCard
          recommendation={primary}
          isPrimary
          onFeedback={(type) => onFeedback(primary.material.material_id, type)}
          feedbackDisabled={
            feedbackLoading &&
            feedbackMaterialId === primary.material.material_id
          }
        />
      )}

      {secondary.length > 0 && (
        <div style={styles.secondaryTitle}>Дальше по траектории</div>
      )}

      {secondary.map((rec) => (
        <MaterialCard key={rec.material.material_id} recommendation={rec} />
      ))}

      {feedbackLoading && (
        <div style={styles.recalculating}>
          <Spin size="small" />
          <span>Сохраняем вашу обратную связь...</span>
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  centered: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: 60,
    gap: 16,
  },
  loadingText: { color: "#6B7280", fontSize: 14 },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: "#0B0B0B",
    marginBottom: 16,
  },
  secondaryTitle: {
    fontSize: 14,
    fontWeight: 600,
    color: "#6B7280",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginTop: 24,
    marginBottom: 12,
  },
  recalculating: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: 14,
    background: "#FEECEA",
    borderRadius: 10,
    marginTop: 16,
    fontSize: 13,
    color: "#0B0B0B",
  },
};
