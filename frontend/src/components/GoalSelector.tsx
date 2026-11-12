import React from "react";
import { Select } from "antd";
import type { BusinessGoal } from "../types";

interface GoalSelectorProps {
  goals: BusinessGoal[];
  selectedGoalId: string;
  onGoalChange: (goalId: string) => void;
}

export const GoalSelector: React.FC<GoalSelectorProps> = ({
  goals,
  selectedGoalId,
  onGoalChange,
}) => {
  const currentGoal = goals.find((g) => g.id === selectedGoalId);

  return (
    <div style={styles.container}>
      <div style={styles.label}>Ваша бизнес-цель</div>
      <div style={styles.row}>
        <Select
          value={selectedGoalId}
          onChange={onGoalChange}
          style={{ width: "100%", maxWidth: 480 }}
          size="large"
          options={goals.map((g) => ({ value: g.id, label: g.title }))}
        />
      </div>
      {currentGoal && (
        <div style={styles.description}>{currentGoal.description}</div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: "#FFFFFF",
    borderRadius: 12,
    padding: "20px 24px",
    marginBottom: 24,
    border: "1px solid #E5E5E5",
  },
  label: {
    fontSize: 12,
    color: "#6B7280",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 8,
    fontWeight: 500,
  },
  row: { display: "flex", alignItems: "center", gap: 12 },
  description: { fontSize: 13, color: "#6B7280", marginTop: 8 },
};
