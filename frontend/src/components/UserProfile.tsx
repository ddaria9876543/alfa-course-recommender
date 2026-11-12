import React from "react";
import { Tag } from "antd";
import type { DemoUser } from "../types";

interface UserProfileProps {
  user: DemoUser | null;
}

const levelLabels: Record<string, string> = {
  beginner: "Начинающий",
  intermediate: "Продолжающий",
  advanced: "Продвинутый",
};

export const UserProfile: React.FC<UserProfileProps> = ({ user }) => {
  if (!user) return <div style={styles.empty}>Профиль не выбран</div>;

  return (
    <div style={styles.container}>
      <div style={styles.avatar}>{user.avatar_initials}</div>
      <div style={styles.name}>{user.name}</div>
      <div style={styles.level}>Уровень: {levelLabels[user.level]}</div>

      <div style={styles.section}>
        <div style={styles.sectionTitle}>История обучения</div>
        <div style={styles.sectionText}>
          {user.has_history ? (
            <>
              <div style={styles.historyStatus}>
                ✓ Есть история взаимодействий
              </div>
              <div style={styles.historySummary}>{user.history_summary}</div>
              {user.completed_materials.length > 0 && (
                <div style={styles.completed}>
                  Пройдено материалов: {user.completed_materials.length}
                </div>
              )}
            </>
          ) : (
            <div style={styles.noHistory}>
              История отсутствует. Рекомендации строятся только на основе
              бизнес-цели.
            </div>
          )}
        </div>
      </div>

      <div style={styles.section}>
        <div style={styles.sectionTitle}>Интересы</div>
        <div style={styles.interests}>
          {user.interests.length > 0 ? (
            user.interests.map((interest) => (
              <Tag key={interest}>{interest}</Tag>
            ))
          ) : (
            <div style={styles.noData}>Не указаны</div>
          )}
        </div>
      </div>

      <div style={styles.section}>
        <div style={styles.sectionTitle}>Факторы персонализации</div>
        <div style={styles.factorsList}>
          <div style={styles.factor}>✓ Бизнес-цель пользователя</div>
          {user.has_history && (
            <>
              <div style={styles.factor}>✓ История взаимодействий</div>
              <div style={styles.factor}>✓ Тематические интересы</div>
              <div style={styles.factor}>✓ Уровень подготовки</div>
            </>
          )}
          <div style={styles.factor}>✓ Обратная связь по материалам</div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: "#FFFFFF",
    borderRadius: 12,
    padding: 24,
    border: "1px solid #E5E5E5",
    height: "fit-content",
    position: "sticky",
    top: 24,
  },
  empty: { color: "#6B7280", padding: 20, textAlign: "center" },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: "50%",
    background: "#F5F5F5",
    color: "#0B0B0B",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 22,
    fontWeight: 700,
    margin: "0 auto 12px",
  },
  name: { fontSize: 16, fontWeight: 600, textAlign: "center", marginBottom: 4 },
  level: {
    fontSize: 13,
    color: "#6B7280",
    textAlign: "center",
    marginBottom: 20,
  },
  section: {
    marginBottom: 20,
    paddingBottom: 16,
    borderBottom: "1px solid #F5F5F5",
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: 600,
    color: "#6B7280",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: 8,
  },
  sectionText: { fontSize: 13, color: "#374151", lineHeight: 1.5 },
  historyStatus: {
    fontSize: 13,
    color: "#10B981",
    fontWeight: 500,
    marginBottom: 6,
  },
  historySummary: {
    fontSize: 12,
    color: "#6B7280",
    lineHeight: 1.5,
    marginBottom: 6,
  },
  completed: { fontSize: 12, color: "#0B0B0B", fontWeight: 500 },
  noHistory: { fontSize: 12, color: "#6B7280", fontStyle: "italic" },
  interests: { display: "flex", flexWrap: "wrap", gap: 6 },
  noData: { fontSize: 12, color: "#9CA3AF" },
  factorsList: { display: "flex", flexDirection: "column", gap: 4 },
  factor: { fontSize: 12, color: "#374151" },
};
