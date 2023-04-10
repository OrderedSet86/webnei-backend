import psycopg2
import psycopg2.pool
from contextlib import contextmanager

import load_env
from src.graphql.core.config import settings

dbpool = psycopg2.pool.ThreadedConnectionPool(
    host=settings.HOST_URL,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    minconn=30,
    maxconn=30,
)

@contextmanager
def db_cursor():
    conn = dbpool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
            conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        dbpool.putconn(conn)