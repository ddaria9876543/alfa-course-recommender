
import React, { useState } from "react";
import {
  Button,
  Input,
  Select,
  Steps,
  Typography,
  message,
} from "antd";

import type { BusinessGoal } from "../types";

const { Title, Text } = Typography;

export interface OnboardingAnswers {
  goalIds: string[];
  customGoal: string;
  industry?: string;
  businessStage?: "planning" | "running";
  experience?: "beginner" | "experienced";
  preferredFormats: ("article" | "course" | "document")[];
}

interface OnboardingProps {
  goals: BusinessGoal[];
  onSubmit: (answers: OnboardingAnswers) => void;
}

const industryOptions = [
  { value: "интернет-магазин", label: "Интернет-магазин / маркетплейсы" },
  { value: "розница", label: "Розничная торговля" },
  { value: "красота", label: "Красота и уход" },
  { value: "кафе", label: "Кафе и рестораны" },
  { value: "производство", label: "Производство" },
  { value: "услуги", label: "Сфера услуг" },
  { value: "строительство", label: "Строительство и недвижимость" },
  { value: "логистика", label: "Транспорт и логистика" },
];

const stageOptions = [
  { value: "planning", label: "Планирую открыть бизнес" },
  { value: "running", label: "Уже веду бизнес" },
];

const experienceOptions = [
  { value: "beginner", label: "Только начинаю разбираться" },
  { value: "experienced", label: "Уже разбираюсь в теме" },
];

const formatOptions = [
  { value: "article", label: "Статьи" },
  { value: "course", label: "Курсы" },
  { value: "document", label: "Документы и шаблоны" },
];

export const Onboarding: React.FC<OnboardingProps> = ({
  goals,
  onSubmit,
}) => {
  const [currentStep, setCurrentStep] = useState(0);

  const [selectedGoalIds, setSelectedGoalIds] = useState<string[]>([]);
  const [customGoal, setCustomGoal] = useState("");

  const [industry, setIndustry] = useState<string | undefined>();
  const [businessStage, setBusinessStage] = useState<
    "planning" | "running" | undefined
  >();

  const [experience, setExperience] = useState<
    "beginner" | "experienced" | undefined
  >();

  const [preferredFormats, setPreferredFormats] = useState<
    ("article" | "course" | "document")[]
  >([]);

  const hasCustomGoal = customGoal.trim().length > 0;

  const selectedGoalsCount =
    selectedGoalIds.length + (hasCustomGoal ? 1 : 0);

  const handleGoalsChange = (values: string[]) => {
    const maxReadyGoals = hasCustomGoal ? 2 : 3;

    if (values.length > maxReadyGoals) {
      message.warning("Можно выбрать не более трёх целей");
      return;
    }

    setSelectedGoalIds(values);
  };

  const handleCustomGoalChange = (value: string) => {
    if (
      !customGoal.trim() &&
      value.trim() &&
      selectedGoalIds.length >= 3
    ) {
      message.warning(
        "Сначала уберите одну из готовых целей",
      );
      return;
    }

    setCustomGoal(value);
  };

  const handleNext = () => {
    if (selectedGoalsCount === 0) {
      message.warning("Выберите хотя бы одну бизнес-цель");
      return;
    }

    setCurrentStep(1);
  };

  const handleSubmit = () => {
    if (selectedGoalsCount === 0 || selectedGoalsCount > 3) {
      message.warning("Выберите от одной до трёх целей");
      return;
    }

    onSubmit({
      goalIds: selectedGoalIds,
      customGoal: customGoal.trim(),
      industry,
      businessStage,
      experience,
      preferredFormats,
    });
  };

  return (
    <div style={styles.page}>
      <div style={styles.intro}>
        <Text style={styles.eyebrow}>
          ПЕРСОНАЛЬНОЕ ОБУЧЕНИЕ ДЛЯ ПРЕДПРИНИМАТЕЛЕЙ
        </Text>

        <Title level={2} style={styles.title}>
          Найдём полезные материалы для вашего бизнеса
        </Title>

        <Text style={styles.subtitle}>
          Ответьте на несколько вопросов, и Альфа-Путь
          подберёт статьи, курсы и инструкции под ваши задачи.
        </Text>
      </div>

      <div style={styles.card}>
        <Steps
          current={currentStep}
          size="small"
          responsive
          items={[
            { title: "О вашем бизнесе" },
            { title: "Ваши предпочтения" },
          ]}
          style={{ marginBottom: 32 }}
        />

        {currentStep === 0 && (
          <div>
            <Title level={4} style={styles.stepTitle}>
              Расскажите о своём бизнесе
            </Title>

            <div style={styles.field}>
              <Text style={styles.label}>
                Какие задачи хотите решить?
              </Text>

              <Text style={styles.hint}>
                Можно выбрать до трёх целей.
                Для каждой мы подготовим отдельную подборку.
              </Text>

              <Select
                mode="multiple"
                allowClear
                size="large"
                style={{ width: "100%" }}
                placeholder="Выберите бизнес-цели"
                value={selectedGoalIds}
                onChange={handleGoalsChange}
                options={goals.map((goal) => ({
                  value: goal.id,
                  label: goal.title,
                }))}
                optionFilterProp="label"
                maxTagCount="responsive"
              />

              <div style={styles.counter}>
                Выбрано целей: {selectedGoalsCount} из 3
              </div>
            </div>

            <div style={styles.field}>
              <Text style={styles.label}>
                Или опишите свою бизнес-задачу
              </Text>

              <Text style={styles.hint}>
                Например, если подходящего варианта нет в списке.
                Собственная задача тоже считается отдельной целью.
              </Text>

              <Input.TextArea
                rows={3}
                maxLength={500}
                showCount
                value={customGoal}
                onChange={(event) =>
                  handleCustomGoalChange(event.target.value)
                }
                placeholder="Например: хочу увеличить повторные продажи в салоне красоты"
              />
            </div>

            <div style={styles.field}>
              <Text style={styles.label}>
                В какой сфере работает ваш бизнес?
              </Text>

              <Select
                size="large"
                allowClear
                style={{ width: "100%" }}
                placeholder="Выберите сферу (необязательно)"
                value={industry}
                onChange={setIndustry}
                options={industryOptions}
              />
            </div>

            <div style={styles.field}>
              <Text style={styles.label}>
                На каком этапе находится ваш бизнес?
              </Text>

              <Select
                size="large"
                allowClear
                style={{ width: "100%" }}
                placeholder="Выберите этап (необязательно)"
                value={businessStage}
                onChange={setBusinessStage}
                options={stageOptions}
              />
            </div>

            <div style={styles.actions}>
              <Button
                type="primary"
                size="large"
                onClick={handleNext}
                disabled={selectedGoalsCount === 0}
              >
                Продолжить
              </Button>
            </div>
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <Title level={4} style={styles.stepTitle}>
              Настроим обучение под вас
            </Title>

            <Text style={styles.hint}>
              Эти вопросы необязательны.
              Они помогут точнее подобрать материалы.
            </Text>

            <div style={{ ...styles.field, marginTop: 24 }}>
              <Text style={styles.label}>
                Насколько хорошо вы разбираетесь в выбранных темах?
              </Text>

              <Select
                size="large"
                allowClear
                style={{ width: "100%" }}
                placeholder="Выберите уровень (необязательно)"
                value={experience}
                onChange={setExperience}
                options={experienceOptions}
              />
            </div>

            <div style={styles.field}>
              <Text style={styles.label}>
                Какие форматы обучения вам удобны?
              </Text>

              <Text style={styles.hint}>
                Можно выбрать несколько.
                Если ничего не выбрать, учтём все форматы.
              </Text>

              <Select
                mode="multiple"
                allowClear
                size="large"
                style={{ width: "100%" }}
                placeholder="Любые форматы"
                value={preferredFormats}
                onChange={(values) =>
                  setPreferredFormats(
                    values as (
                      | "article"
                      | "course"
                      | "document"
                    )[],
                  )
                }
                options={formatOptions}
              />
            </div>

            <div style={styles.summary}>
              <Text strong>
                Ваша будущая подборка
              </Text>

              <Text style={styles.summaryText}>
                Бизнес-целей: {selectedGoalsCount}
              </Text>

              <Text style={styles.summaryText}>
                Форматы:{" "}
                {preferredFormats.length > 0
                  ? formatOptions
                      .filter((format) =>
                        preferredFormats.includes(
                          format.value as
                            | "article"
                            | "course"
                            | "document",
                        ),
                      )
                      .map((format) => format.label)
                      .join(", ")
                  : "Любые"}
              </Text>

              <Text style={styles.summaryText}>
                Сфера:{" "}
                {industryOptions.find(
                  (option) => option.value === industry,
                )?.label || "Не указана"}
              </Text>
            </div>

            <div style={styles.actions}>
              <Button
                size="large"
                onClick={() => setCurrentStep(0)}
              >
                Назад
              </Button>

              <Button
                size="large"
                type="primary"
                onClick={handleSubmit}
              >
                Получить рекомендации
              </Button>
            </div>
          </div>
        )}
      </div>

      <div style={styles.bottomHint}>
        Подбираем материалы из каталога Альфа-Курса
        с учётом ваших целей и предпочтений.
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: 760,
    margin: "0 auto",
    padding: "40px 20px 64px",
  },

  intro: {
    textAlign: "center",
    marginBottom: 32,
  },

  eyebrow: {
    display: "block",
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 1,
    color: "#EF3124",
    marginBottom: 12,
  },

  title: {
    marginBottom: 12,
    lineHeight: 1.25,
  },

  subtitle: {
    display: "block",
    fontSize: 15,
    color: "#64748B",
    lineHeight: 1.6,
  },

  card: {
    background: "#FFFFFF",
    border: "1px solid #E5E7EB",
    borderRadius: 16,
    padding: 32,
    boxShadow: "0 8px 32px rgba(15, 23, 42, 0.04)",
  },

  stepTitle: {
    marginBottom: 24,
  },

  field: {
    marginBottom: 28,
  },

  label: {
    display: "block",
    fontSize: 14,
    fontWeight: 600,
    color: "#111827",
    marginBottom: 8,
  },

  hint: {
    display: "block",
    fontSize: 13,
    color: "#64748B",
    lineHeight: 1.5,
    marginBottom: 10,
  },

  counter: {
    fontSize: 12,
    color: "#94A3B8",
    marginTop: 8,
    textAlign: "right",
  },

  actions: {
    display: "flex",
    justifyContent: "flex-end",
    gap: 12,
    marginTop: 32,
  },

  summary: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    padding: 20,
    background: "#F8FAFC",
    borderRadius: 12,
    marginTop: 28,
  },

  summaryText: {
    fontSize: 13,
    color: "#64748B",
  },

  bottomHint: {
    textAlign: "center",
    color: "#94A3B8",
    fontSize: 12,
    marginTop: 24,
  },
};
