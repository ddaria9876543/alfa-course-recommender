
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB", "alfa_course"),
        user=os.getenv("POSTGRES_USER", "alfa_user"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5434"),
    )