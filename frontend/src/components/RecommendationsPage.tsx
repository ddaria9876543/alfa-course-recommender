
import React, { useState } from "react";

import {
  Alert,
  Button,
  Empty,
  Select,
  Spin,
  Tabs,
  Tag,
  Typography,
} from "antd";

import type {
  Route,
  Recommendation,
  FeedbackType,
  MaterialType,
} from "../types";

const { Title, Text, Paragraph } = Typography;

const PAGE_SIZE = 6;

export interface RecommendationGroup {
  goalId: string;
  goalTitle: string;
  route: Route;
}

interface RecommendationsPageProps {
  groups: RecommendationGroup[];
  loading: boolean;
  error: string | null;
  feedbackLoading: boolean;
  feedbackMaterialId: string | null;
  onFeedback: (
    goalId: string,
    materialId: string,
    type: FeedbackType,
  ) => void;
  onEditAnswers: () => void;
}

type FormatFilter = "all" | MaterialType;

const formatLabels: Record<MaterialType, string> = {
  article: "Статья",
  course: "Курс",
  document: "Документ",
};

const formatColors: Record<MaterialType, string> = {
  article: "blue",
  course: "red",
  document: "green",
};

const feedbackOptions: {
  label: string;
  value: FeedbackType;
}[] = [
  {
    label: "Уже знаю эту тему",
    value: "already_know",
  },
  {
    label: "Слишком сложно",
    value: "too_hard",
  },
  {
    label: "Неактуально для меня",
    value: "irrelevant",
  },
];

function materialWord(count: number): string {
  const lastTwo = count % 100;
  const last = count % 10;

  if (lastTwo >= 11 && lastTwo <= 14) {
    return "материалов";
  }

  if (last === 1) {
    return "материал";
  }

  if (last >= 2 && last <= 4) {
    return "материала";
  }

  return "материалов";
}

export const RecommendationsPage: React.FC<
  RecommendationsPageProps
> = ({
  groups,
  loading,
  error,
  feedbackLoading,
  feedbackMaterialId,
  onFeedback,
  onEditAnswers,
}) => {
  const [activeGoalId, setActiveGoalId] = useState("");
  const [formatFilter, setFormatFilter] =
    useState<FormatFilter>("all");
  const [visibleCount, setVisibleCount] =
    useState(PAGE_SIZE);

  // Активная вкладка бизнес-цели.
  const activeGroup =
    groups.find((group) => group.goalId === activeGoalId) ||
    groups[0];

  const recommendations =
    activeGroup?.route.recommendations || [];

  // Фильтрация внутри выбранной цели.
  const filteredRecommendations = recommendations.filter(
    (item) =>
      formatFilter === "all" ||
      item.material.material_type === formatFilter,
  );

  // Показываем первые 6, затем 12, 18 и так далее.
  const visibleRecommendations =
    filteredRecommendations.slice(0, visibleCount);

  const hasMore =
    visibleCount < filteredRecommendations.length;

  const remainingCount = Math.max(
    0,
    filteredRecommendations.length -
      visibleRecommendations.length,
  );

  const nextCount = Math.min(
    PAGE_SIZE,
    remainingCount,
  );

  const handleGoalChange = (goalId: string) => {
    setActiveGoalId(goalId);
    setFormatFilter("all");
    setVisibleCount(PAGE_SIZE);
  };

  const handleFormatChange = (
    value: FormatFilter,
  ) => {
    setFormatFilter(value);
    setVisibleCount(PAGE_SIZE);
  };

  const handleShowMore = () => {
    setVisibleCount((previous) =>
      previous + PAGE_SIZE,
    );
  };

  const renderMaterial = (item: Recommendation) => {
    const material = item.material;

    const isUpdating =
      feedbackLoading &&
      feedbackMaterialId === material.material_id;

    return (
      <div
        key={material.material_id}
        style={styles.materialCard}
      >
        {/* Формат и темы */}
        <div style={styles.tags}>
          <Tag
            color={formatColors[material.material_type]}
          >
            {formatLabels[material.material_type]}
          </Tag>

          {material.topics.slice(0, 2).map((topic) => (
            <Tag key={topic}>{topic}</Tag>
          ))}
        </div>

        {/* Название */}
        <Title
          level={4}
          style={styles.materialTitle}
        >
          {material.title}
        </Title>

        {/* Описание */}
        {material.description && (
          <Paragraph
            ellipsis={{
              rows: 3,
              expandable: true,
              symbol: "Подробнее",
            }}
            style={styles.description}
          >
            {material.description}
          </Paragraph>
        )}

        {/* Объяснение */}
        {item.explanation && (
          <div style={styles.explanation}>
            <Text
              strong
              style={styles.explanationTitle}
            >
              Почему рекомендуем
            </Text>

            <Text style={styles.explanationText}>
              {item.explanation}
            </Text>

            {item.reason_factors.length > 0 && (
              <div style={styles.factors}>
                {item.reason_factors
                  .filter(
                    (factor) =>
                      factor !== item.explanation,
                  )
                  .slice(0, 2)
                  .map((factor, index) => (
                    <Text
                      key={`${factor}-${index}`}
                      style={styles.factor}
                    >
                      • {factor}
                    </Text>
                  ))}
              </div>
            )}
          </div>
        )}

        {/* Действия */}
        <div style={styles.materialActions}>
          <Button
            type="primary"
            href={material.url || undefined}
            target="_blank"
            rel="noopener noreferrer"
            disabled={!material.url}
            style={{
              ...styles.openButton,
              ...(!material.url
                ? styles.disabledButton
                : {}),
            }}
          >
            Открыть материал
          </Button>

          <Select<FeedbackType>
            placeholder="Не подходит?"
            style={styles.feedbackSelect}
            value={undefined}
            disabled={feedbackLoading}
            onChange={(type) => {
              if (!activeGroup) return;

              onFeedback(
                activeGroup.goalId,
                material.material_id,
                type,
              );

              // После обратной связи оставляем
              // текущую вкладку и количество
              // открытых карточек без изменений.
            }}
            options={feedbackOptions}
          />
        </div>

        {isUpdating && (
          <div style={styles.feedbackStatus}>
            <Spin size="small" />
            <Text type="secondary">
              Обновляем рекомендации...
            </Text>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={styles.page}>
      {/* Шапка страницы */}
      <div style={styles.heading}>
        <div>
          <Text style={styles.eyebrow}>
            ВАША ПЕРСОНАЛЬНАЯ ПОДБОРКА
          </Text>

          <Title level={2} style={styles.title}>
            Материалы для вашего бизнеса
          </Title>

          <Text style={styles.subtitle}>
            Мы подобрали материалы под ваши цели.
            Переключайтесь между задачами
            и выбирайте удобный формат обучения.
          </Text>
        </div>

        <Button
          size="large"
          onClick={onEditAnswers}
          style={styles.editButton}
        >
          Изменить ответы
        </Button>
      </div>

      {/* Загрузка */}
      {loading && (
        <div style={styles.centered}>
          <Spin size="large" />
          <Text type="secondary">
            Подбираем материалы под ваши бизнес-задачи...
          </Text>
        </div>
      )}

      {/* Ошибка API */}
      {error && (
        <Alert
          type="error"
          showIcon
          message="Не удалось загрузить рекомендации"
          description={error}
          style={{ marginBottom: 24 }}
        />
      )}

      {/* Результаты */}
      {!loading && groups.length > 0 && (
        <>
          {/* Общая информация */}
          <div style={styles.summary}>
            <div>
              <Text style={styles.summaryLabel}>
                ВЫБРАНО БИЗНЕС-ЦЕЛЕЙ
              </Text>

              <div style={styles.summaryNumber}>
                {groups.length}
              </div>
            </div>

            <div>
              <Text style={styles.summaryLabel}>
                МАТЕРИАЛОВ В ТЕКУЩЕЙ ПОДБОРКЕ
              </Text>

              <div style={styles.summaryNumber}>
                {recommendations.length}
              </div>
            </div>
          </div>

          <div style={styles.resultsCard}>
            <Text style={styles.sectionLabel}>
              РЕКОМЕНДАЦИИ ПО ВАШИМ ЦЕЛЯМ
            </Text>

            {/* Отдельная вкладка для каждой цели */}
            <Tabs
              activeKey={activeGroup?.goalId}
              onChange={handleGoalChange}
              items={groups.map((group) => ({
                key: group.goalId,
                label: group.goalTitle,
              }))}
            />

            {/* Выбранная цель и фильтр */}
            <div style={styles.filters}>
              <div>
                <Title
                  level={4}
                  style={styles.currentGoalTitle}
                >
                  {activeGroup?.goalTitle}
                </Title>

                <Text type="secondary">
                  В подборке:{" "}
                  {recommendations.length}{" "}
                  {materialWord(recommendations.length)}
                </Text>
              </div>

              <Select<FormatFilter>
                style={styles.formatSelect}
                value={formatFilter}
                onChange={handleFormatChange}
                options={[
                  {
                    value: "all",
                    label: "Все форматы",
                  },
                  {
                    value: "article",
                    label: "Статьи",
                  },
                  {
                    value: "course",
                    label: "Курсы",
                  },
                  {
                    value: "document",
                    label: "Документы",
                  },
                ]}
              />
            </div>

            {/* Число результатов после фильтрации */}
            <div style={styles.resultsCount}>
              <Text type="secondary">
                Показано{" "}
                {visibleRecommendations.length} из{" "}
                {filteredRecommendations.length}{" "}
                {materialWord(
                  filteredRecommendations.length,
                )}
              </Text>
            </div>

            {/* Карточки */}
            <div style={styles.materialList}>
              {visibleRecommendations.length > 0 ? (
                visibleRecommendations.map(
                  renderMaterial,
                )
              ) : (
                <div style={styles.emptyList}>
                  <Empty
                    description={
                      "В этой подборке нет материалов выбранного формата"
                    }
                  />
                </div>
              )}
            </div>

            {/* Пагинация */}
            {hasMore && (
              <div style={styles.showMoreContainer}>
                <Button
                  size="large"
                  onClick={handleShowMore}
                  style={styles.showMoreButton}
                >
                  Показать ещё {nextCount}
                </Button>

                <Text style={styles.remainingText}>
                  Осталось: {remainingCount}{" "}
                  {materialWord(remainingCount)}
                </Text>
              </div>
            )}

            <Text style={styles.bottomNote}>
              Материалы упорядочены по оценке
              рекомендательной системы.
              Сейчас показываем до 30 кандидатов
              для каждой бизнес-цели.
            </Text>
          </div>
        </>
      )}

      {/* Нет данных */}
      {!loading && !error && groups.length === 0 && (
        <Empty
          description="Рекомендации пока не сформированы"
          style={{ padding: 60 }}
        >
          <Button
            type="primary"
            onClick={onEditAnswers}
            style={styles.openButton}
          >
            Вернуться к опросу
          </Button>
        </Empty>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: 1100,
    margin: "0 auto",
    padding: "32px 20px 64px",
  },

  heading: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    flexWrap: "wrap",
    gap: 20,
    marginBottom: 28,
  },

  eyebrow: {
    display: "block",
    color: "#EF3124",
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 1,
    marginBottom: 8,
  },

  title: {
    marginBottom: 10,
    color: "#111827",
  },

  subtitle: {
    display: "block",
    maxWidth: 680,
    color: "#64748B",
    fontSize: 14,
    lineHeight: 1.6,
  },

  editButton: {
    borderRadius: 8,
    fontWeight: 500,
  },

  summary: {
    display: "flex",
    flexWrap: "wrap",
    gap: 40,
    background: "#FFFFFF",
    border: "1px solid #E5E7EB",
    borderRadius: 14,
    padding: 24,
    marginBottom: 24,
  },

  summaryLabel: {
    display: "block",
    color: "#64748B",
    fontSize: 11,
    fontWeight: 600,
    marginBottom: 6,
  },

  summaryNumber: {
    fontSize: 28,
    fontWeight: 700,
    color: "#111827",
  },

  resultsCard: {
    background: "#FFFFFF",
    border: "1px solid #E5E7EB",
    borderRadius: 14,
    padding: 24,
  },

  sectionLabel: {
    display: "block",
    fontSize: 12,
    color: "#64748B",
    fontWeight: 600,
    marginBottom: 16,
  },

  filters: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: 16,
    marginTop: 16,
    marginBottom: 24,
  },

  currentGoalTitle: {
    margin: 0,
    color: "#111827",
  },

  formatSelect: {
    minWidth: 190,
  },

  resultsCount: {
    marginBottom: 16,
    fontSize: 13,
  },

  materialList: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(min(100%, 280px), 1fr))",
    gap: 16,
  },

  materialCard: {
    display: "flex",
    flexDirection: "column",
    background: "#FFFFFF",
    border: "1px solid #E5E7EB",
    borderRadius: 12,
    padding: 20,
    minWidth: 0,
  },

  tags: {
    display: "flex",
    flexWrap: "wrap",
    gap: 4,
    marginBottom: 12,
  },

  materialTitle: {
    fontSize: 17,
    lineHeight: 1.4,
    marginBottom: 12,
    color: "#111827",
  },

  description: {
    fontSize: 13,
    color: "#64748B",
    lineHeight: 1.6,
    marginBottom: 16,
  },

  explanation: {
    display: "flex",
    flexDirection: "column",
    gap: 6,
    padding: 12,
    background: "#F8FAFC",
    borderRadius: 8,
    marginTop: "auto",
    marginBottom: 16,
  },

  explanationTitle: {
    fontSize: 12,
    color: "#111827",
  },

  explanationText: {
    fontSize: 12,
    color: "#64748B",
    lineHeight: 1.5,
  },

  factors: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
    marginTop: 6,
  },

  factor: {
    fontSize: 12,
    color: "#64748B",
  },

  materialActions: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    gap: 10,
    paddingTop: 12,
    marginTop: "auto",
  },

  openButton: {
    backgroundColor: "#EF3124",
    borderColor: "#EF3124",
    color: "#FFFFFF",
    fontWeight: 600,
    borderRadius: 8,
    minHeight: 34,
  },

  disabledButton: {
    backgroundColor: "#F3F4F6",
    borderColor: "#E5E7EB",
    color: "#9CA3AF",
  },

  feedbackSelect: {
    width: 190,
    maxWidth: "100%",
  },

  feedbackStatus: {
    display: "flex",
    gap: 8,
    alignItems: "center",
    marginTop: 10,
  },

  showMoreContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 10,
    marginTop: 28,
  },

  showMoreButton: {
    borderRadius: 8,
    fontWeight: 600,
    minWidth: 200,
  },

  remainingText: {
    fontSize: 12,
    color: "#94A3B8",
  },

  emptyList: {
    gridColumn: "1 / -1",
    padding: 40,
  },

  centered: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 16,
    padding: 80,
  },

  bottomNote: {
    display: "block",
    color: "#94A3B8",
    fontSize: 12,
    marginTop: 24,
    lineHeight: 1.5,
  },
};
