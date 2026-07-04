import json
import time
import os
import logging
import redis
import psycopg2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [WORKER] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)


def get_redis(retries=10):
    for i in range(retries):
        try:
            r = redis.Redis(host='redis', db=0, socket_connect_timeout=5)
            r.ping()
            log.info('✅ Connected to Redis')
            return r
        except Exception as e:
            log.warning(f'⏳ Redis not ready ({i+1}/{retries}): {e}')
            time.sleep(2)
    raise Exception('Could not connect to Redis')


def get_db(retries=15):
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host='db',
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
                dbname=os.getenv('POSTGRES_DB', 'postgres'),
            )
            conn.autocommit = True
            log.info('✅ Connected to PostgreSQL')
            return conn
        except Exception as e:
            log.warning(f'⏳ DB not ready ({i+1}/{retries}): {e}')
            time.sleep(3)
    raise Exception('Could not connect to PostgreSQL')


def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id    VARCHAR(255) NOT NULL UNIQUE,
                vote  VARCHAR(255) NOT NULL
            )
        """)
    log.info('✅ Votes table ready')


def process_vote(conn, voter_id, vote):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO votes (id, vote) VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET vote = EXCLUDED.vote
        """, (voter_id, vote))
    log.info(f'📝 Vote recorded: {voter_id[:8]}... → {vote}')


def main():
    log.info('🚀 Worker starting...')

    r = get_redis()
    conn = get_db()
    ensure_table(conn)

    log.info('👂 Listening for votes on Redis queue...')

    while True:
        try:
            # Block until a vote arrives (timeout 0 = forever)
            _, data = r.blpop('votes', timeout=0)
            vote_data = json.loads(data)

            voter_id = vote_data['voter_id']
            vote     = vote_data['vote']

            process_vote(conn, voter_id, vote)

        except psycopg2.OperationalError:
            log.error('DB connection lost — reconnecting...')
            conn = get_db()
            ensure_table(conn)

        except redis.RedisError:
            log.error('Redis connection lost — reconnecting...')
            r = get_redis()

        except Exception as e:
            log.error(f'Unexpected error: {e}')
            time.sleep(1)


if __name__ == '__main__':
    main()
