import React from "react";
import { Select } from "antd";
import type { DemoUser } from "../types";

interface HeaderProps {
  users: DemoUser[];
  selectedUserId: string;
  onUserChange: (userId: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  users,
  selectedUserId,
  onUserChange,
}) => {
  const currentUser = users.find((u) => u.user_id === selectedUserId);

  return (
    <header style={styles.header}>
      <div style={styles.left}>
        <div style={styles.logo}>
          <div style={styles.logoIcon}>А</div>
          <div>
            <div style={styles.logoTitle}>Альфа-Путь</div>
            <div style={styles.logoSubtitle}>
              Образовательный навигатор для предпринимателей
            </div>
          </div>
        </div>
      </div>

      <div style={styles.right}>
        <div style={styles.userLabel}>Демонстрационный пользователь:</div>
        <Select
          value={selectedUserId}
          onChange={onUserChange}
          style={{ width: 340 }}
          dropdownMatchSelectWidth={false}
          options={users.map((u) => ({
            value: u.user_id,
            label: (
              <span
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  minWidth: 260,
                }}
              >
                <span style={styles.avatarSmall}>{u.avatar_initials}</span>
                {u.name}
                {u.has_history && (
                  <span style={styles.historyBadge}>с историей</span>
                )}
              </span>
            ),
          }))}
        />
        {currentUser && (
          <div style={styles.userHint}>
            {currentUser.has_history
              ? "Учитывается история обучения"
              : "Холодный старт — только бизнес-цель"}
          </div>
        )}
      </div>
    </header>
  );
};

const styles: Record<string, React.CSSProperties> = {
  header: {
    background: "#FFFFFF",
    borderBottom: "1px solid #E5E5E5",
    padding: "16px 32px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 16,
  },
  left: {
    display: "flex",
    alignItems: "center",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  logoIcon: {
    width: 40,
    height: 40,
    borderRadius: 8,
    background: "#EF3124",
    color: "#FFFFFF",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
    fontSize: 20,
  },
  logoTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#0B0B0B",
    lineHeight: 1.2,
  },
  logoSubtitle: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 2,
  },
  right: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end",
    gap: 4,
  },
  userLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 2,
  },
  userHint: {
    fontSize: 11,
    color: "#6B7280",
    marginTop: 2,
  },
  avatarSmall: {
    width: 24,
    height: 24,
    borderRadius: "50%",
    background: "#F5F5F5",
    color: "#0B0B0B",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 10,
    fontWeight: 600,
  },
  historyBadge: {
    fontSize: 10,
    color: "#EF3124",
    background: "#FEECEA",
    padding: "2px 6px",
    borderRadius: 4,
  },
};
