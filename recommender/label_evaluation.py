
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "reports"
SOURCE = BASE_DIR / "manual_relevance.csv"
OUTPUT = BASE_DIR / "manual_relevance_labeled.csv"

# Оценки соответствуют slug из CSV.
# Ключ: профиль, значение: словарь slug -> оценка.

LABELS = {
    "beauty_sales": {
        "a-vse-begut-begut-begut-kak-uderzhat-klientov": 2,
        "ne-my-plohie-a-ty-durak-kak-ne-nado-otvechat-na-otzyvy-v-internete": 1,
        "vozvraty-i-nevykupy-v-chyom-prichina-i-kak-s-nimi-borotsya": 0,
        "gde-i-kak-vesti-uchyot-klientov": 2,
        "dostupnye-analogi-telegrama-dlya-biznesa": 1,
        "kak-pravilno-sostavit-prajs-list": 1,
        "kak-sozdat-programmu-loyalnosti-dlya-klientov-salona-krasoty": 2,
        "kak-uvelichit-povtornye-prodazhi": 2,
        "referalnaya-programma-chto-ehto-takoe-i-kak-sozdat": 2,
        "tekhnika-aktivnogo-slushaniya-v-peregovorah": 1,
    },
    "business_start": {
        "base-dikiy-kak-otkryt-cvetochnuyu-masterskuyu-nichego-ne-znaya-o-biznese": 1,
        "rockme-english-kak-otkryt-odnu-iz-pervyh-foneticheskih-shkol-v-strane": 1,
        "zorca-ceramica-kak-prevratit-miloe-hobbi-v-uspeshnyj-biznes": 1,
        "a-kolya-vyjdet-poshagovaya-instrukciya-po-vyhodu-na-b2b-rynok": 0,
        "biznes-v-sporte-kak-nachat-i-masshtabirovat": 1,
        "kak-otkryt-ip": 2,
        "kak-otkryt-ip-v-moskovskoj-oblasti-poshagovaya-instrukciya": 1,
        "kak-otkryt-ip-onlajn": 2,
        "kak-otkryt-ip-posle-bankrotstva": 1,
        "mozhno-li-otkryt-ip-esli-oficialno-trudoustroen": 1,
    },
    "online_store": {
        "base-dikiy-kak-otkryt-cvetochnuyu-masterskuyu-nichego-ne-znaya-o-biznese": 0,
        "pop-up-magaziny-chto-ehto-i-kak-otkryt": 0,
        "rockme-english-kak-otkryt-odnu-iz-pervyh-foneticheskih-shkol-v-strane": 0,
        "zorca-ceramica-kak-prevratit-miloe-hobbi-v-uspeshnyj-biznes": 0,
        "a-kolya-vyjdet-poshagovaya-instrukciya-po-vyhodu-na-b2b-rynok": 0,
        "biznes-v-sporte-kak-nachat-i-masshtabirovat": 0,
        "internet-marketing-dlya-malogo-biznesa": 2,
        "kak-podklyuchit-onlajn-kassu-k-internet-magazinu-instrukciya": 2,
        "mozhno-li-otkryt-ip-esli-oficialno-trudoustroen": 1,
        "novogodnee-oformlenie-vitrin": 0,
    },
}


def main():
    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not fieldnames or "relevance" not in fieldnames:
        raise ValueError("Missing relevance column")

    for row in rows:
        profile = row["profile"]
        slug = row["slug"]

        if profile not in LABELS or slug not in LABELS[profile]:
            raise ValueError(f"Unknown material: {profile}/{slug}")

        row["relevance"] = LABELS[profile][slug]

    expected = {
        (profile, slug)
        for profile, values in LABELS.items()
        for slug in values
    }
    actual = {(r["profile"], r["slug"]) for r in rows}

    if len(rows) != 30 or actual != expected:
        raise ValueError("Evaluation rows do not match labels")

    with OUTPUT.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Labeled rows: {len(rows)}")
    print(f"Output: {OUTPUT}")
    print("RESULT: SUCCESS")


if __name__ == "__main__":
    main()
