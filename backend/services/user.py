
DEMO_USERS = [
    {
        "id": 1,
        "name": "Анна",
        "role": "Начинающий аналитик",
        "skills": ["Excel", "SQL"],
        "goal": "Изучить Python для анализа данных"
    },
    {
        "id": 2,
        "name": "Виктория",
        "role": "Python-разработчик",
        "skills": ["Python", "Git"],
        "goal": "Освоить машинное обучение"
    },
    {
        "id": 3,
        "name": "Дарья",
        "role": "Начинающий специалист",
        "skills": ["Excel"],
        "goal": "Изучить основы SQL"
    }
]


def get_demo_users():
    return DEMO_USERS


def get_user_by_id(user_id: int):
    for user in DEMO_USERS:
        if user["id"] == user_id:
            return user

    return None
