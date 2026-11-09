
from pathlib import Path
from datetime import datetime
import csv
import subprocess
import sys


# Пути проекта
BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "sql" / "09_data_quality.sql"
REPORTS_DIR = BASE_DIR / "reports"
REPORT_FILE = REPORTS_DIR / "dq_report.csv"

# PostgreSQL в Docker
CONTAINER = "alfa_course_postgres"
DB_USER = "alfa_user"
DB_NAME = "alfa_course"


def run_dq():
    print("ALFA-COURSE | DATA QUALITY")
    print("=" * 65)

    if not SQL_FILE.exists():
        print(f"ERROR: SQL file not found: {SQL_FILE}")
        return 1

    sql = SQL_FILE.read_text(encoding="utf-8-sig")

    command = [
        "docker", "exec", "-i",
        CONTAINER,
        "psql",
        "-X",
        "-v", "ON_ERROR_STOP=1",
        "-U", DB_USER,
        "-d", DB_NAME,
        "-A",
        "-t",
        "-F", "\t",
        "-P", "footer=off",
    ]

    try:
        result = subprocess.run(
            command,
            input=sql,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )

    except FileNotFoundError:
        print("ERROR: Docker command not found")
        return 1

    except subprocess.CalledProcessError as exc:
        print("ERROR: SQL execution failed")
        print(exc.stderr or exc.stdout)
        return 1

    rows = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        parts = line.split("\t")

        if len(parts) != 4:
            print(f"ERROR: Unexpected result: {line}")
            return 1

        check_name, severity, failed_rows, status = parts

        try:
            failed_rows = int(failed_rows)
        except ValueError:
            print("ERROR: Invalid failed_rows value")
            return 1

        rows.append({
            "check_name": check_name,
            "severity": severity,
            "failed_rows": failed_rows,
            "status": status,
        })

    if not rows:
        print("ERROR: No DQ results returned")
        return 1

    print(
        f"{'CHECK':30} "
        f"{'SEVERITY':10} "
        f"{'FAILED':8} STATUS"
    )
    print("-" * 65)

    for row in rows:
        print(
            f"{row['check_name']:30} "
            f"{row['severity']:10} "
            f"{row['failed_rows']:<8} "
            f"{row['status']}"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with REPORT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "check_name",
                "severity",
                "failed_rows",
                "status",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    passed = sum(r["status"] == "PASS" for r in rows)
    warnings = sum(r["status"] == "WARN" for r in rows)
    errors = sum(r["status"] == "FAIL" for r in rows)

    print("-" * 65)
    print(f"PASS: {passed} | WARN: {warnings} | FAIL: {errors}")
    print(f"Report: {REPORT_FILE}")
    print(f"Run time: {datetime.now().isoformat(timespec='seconds')}")

    if errors > 0:
        print("RESULT: FAILED")
        return 1

    print("RESULT: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run_dq())
