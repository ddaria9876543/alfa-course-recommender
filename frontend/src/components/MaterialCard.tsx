import React from "react";
import { Tag, Button } from "antd";
import type { Recommendation, FeedbackType } from "../types";
import { materialTypeLabels } from "../mock/data";

interface MaterialCardProps {
  recommendation: Recommendation;
  isPrimary?: boolean;
  onFeedback?: (type: FeedbackType) => void;
  feedbackDisabled?: boolean;
}

const typeColors: Record<string, string> = {
  article: "#3B82F6",
  course: "#EF3124",
  document: "#10B981",
};

const difficultyLabels: Record<string, string> = {
  beginner: "Начальный",
  intermediate: "Средний",
  advanced: "Продвинутый",
};

export const MaterialCard: React.FC<MaterialCardProps> = ({
  recommendation,
  isPrimary = false,
  onFeedback,
  feedbackDisabled = false,
}) => {
  const { material, step, step_label, score, reason_factors, explanation } =
    recommendation;

  return (
    <div
      style={{
        ...styles.card,
        ...(isPrimary ? styles.primary : {}),
      }}
    >
      <div style={styles.header}>
        <div style={styles.stepBadge}>
          Шаг {step} · {step_label}
        </div>
        <div style={styles.score}>
          Релевантность: {Math.round(score * 100)}%
        </div>
      </div>

      <div style={styles.title}>{material.title}</div>

      <div style={styles.meta}>
        <Tag color={typeColors[material.material_type]}>
          {materialTypeLabels[material.material_type]}
        </Tag>
        {material.difficulty && (
          <Tag>{difficultyLabels[material.difficulty]}</Tag>
        )}
        {material.topics.slice(0, 3).map((t) => (
          <Tag key={t} style={{ background: "#F5F5F5", color: "#6B7280" }}>
            {t}
          </Tag>
        ))}
      </div>

      <div style={styles.description}>{material.description}</div>

      {isPrimary && (
        <div style={styles.explanationBlock}>
          <div style={styles.explanationTitle}>💡 Почему рекомендуем?</div>
          <div style={styles.explanationText}>{explanation}</div>
          <div style={styles.factors}>
            <div style={styles.factorsLabel}>Факторы:</div>
            <div style={styles.factorsList}>
              {reason_factors.map((f, i) => (
                <span key={i} style={styles.factor}>
                  • {f}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Кнопка на ВСЕХ карточках */}
      <div style={styles.actions}>
        <Button
          type="primary"
          size={isPrimary ? "large" : "middle"}
          href={material.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Перейти к материалу →
        </Button>
      </div>

      {isPrimary && onFeedback && (
        <div style={styles.feedbackSection}>
          <div style={styles.feedbackLabel}>Ваша обратная связь:</div>
          <div style={styles.feedbackButtons}>
            <button
              onClick={() => onFeedback("already_know")}
              disabled={feedbackDisabled}
              style={{
                ...styles.feedbackBtn,
                borderColor: "#10B981",
                color: "#10B981",
              }}
            >
              ✓ Уже знаю
            </button>
            <button
              onClick={() => onFeedback("too_hard")}
              disabled={feedbackDisabled}
              style={{
                ...styles.feedbackBtn,
                borderColor: "#F59E0B",
                color: "#F59E0B",
              }}
            >
              ↑ Слишком сложно
            </button>
            <button
              onClick={() => onFeedback("irrelevant")}
              disabled={feedbackDisabled}
              style={{
                ...styles.feedbackBtn,
                borderColor: "#EF3124",
                color: "#EF3124",
              }}
            >
              ✕ Неактуально
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  card: {
    background: "#FFFFFF",
    borderRadius: 12,
    padding: 20,
    border: "1px solid #E5E5E5",
    marginBottom: 12,
  },
  primary: {
    padding: 28,
    border: "2px solid #EF3124",
    boxShadow: "0 4px 20px rgba(239, 49, 36, 0.08)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
    flexWrap: "wrap",
    gap: 8,
  },
  stepBadge: {
    fontSize: 12,
    fontWeight: 600,
    color: "#EF3124",
    background: "#FEECEA",
    padding: "4px 10px",
    borderRadius: 6,
  },
  score: {
    fontSize: 12,
    color: "#6B7280",
  },
  title: {
    fontSize: 18,
    fontWeight: 600,
    color: "#0B0B0B",
    marginBottom: 10,
    lineHeight: 1.3,
  },
  meta: {
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 12,
  },
  description: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 1.5,
    marginBottom: 16,
  },
  explanationBlock: {
    background: "#FAFAFA",
    borderRadius: 10,
    padding: 16,
    marginBottom: 16,
    borderLeft: "3px solid #EF3124",
  },
  explanationTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: "#0B0B0B",
    marginBottom: 6,
  },
  explanationText: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 1.5,
    marginBottom: 10,
  },
  factors: {
    fontSize: 12,
    color: "#6B7280",
  },
  factorsLabel: {
    marginBottom: 4,
    fontWeight: 500,
  },
  factorsList: {
    display: "flex",
    flexDirection: "column",
    gap: 2,
  },
  factor: {
    fontSize: 12,
  },
  actions: {
    display: "flex",
    justifyContent: "flex-start",
    marginTop: 4,
  },
  feedbackSection: {
    marginTop: 20,
    paddingTop: 16,
    borderTop: "1px solid #E5E5E5",
  },
  feedbackLabel: {
    fontSize: 13,
    fontWeight: 500,
    color: "#0B0B0B",
    marginBottom: 10,
  },
  feedbackButtons: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
  },
  feedbackBtn: {
    padding: "8px 14px",
    background: "#FFFFFF",
    border: "1.5px solid",
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 500,
    cursor: "pointer",
  },
};
