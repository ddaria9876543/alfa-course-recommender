import React from "react";
import { Button, Space } from "antd";
import type { FeedbackType } from "../types";

interface FeedbackButtonsProps {
  onFeedback: (type: FeedbackType) => void;
  disabled?: boolean;
  materialTitle: string;
}

const feedbackOptions: {
  type: FeedbackType;
  label: string;
  icon: string;
  color: string;
}[] = [
  { type: "already_know", label: "Уже знаю", icon: "✓", color: "#10B981" },
  { type: "too_hard", label: "Слишком сложно", icon: "↑", color: "#F59E0B" },
  { type: "irrelevant", label: "Неактуально", icon: "✕", color: "#EF3124" },
];

export const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({
  onFeedback,
  disabled,
  materialTitle,
}) => {
  return (
    <div style={styles.container}>
      <div style={styles.question}>Как вам материал «{materialTitle}»?</div>
      <Space wrap size={8}>
        {feedbackOptions.map((opt) => (
          <Button
            key={opt.type}
            onClick={() => onFeedback(opt.type)}
            disabled={disabled}
            style={{
              borderColor: opt.color,
              color: opt.color,
              fontWeight: 500,
            }}
          >
            <span style={{ marginRight: 6 }}>{opt.icon}</span>
            {opt.label}
          </Button>
        ))}
      </Space>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginTop: 16,
    padding: "14px 18px",
    background: "#FAFAFA",
    borderRadius: 10,
    border: "1px dashed #E5E5E5",
  },
  question: {
    fontSize: 13,
    color: "#0B0B0B",
    marginBottom: 10,
    fontWeight: 500,
  },
};
