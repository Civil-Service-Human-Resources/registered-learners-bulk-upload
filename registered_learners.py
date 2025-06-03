from typing import List

from config import get_pg_connection
from csrs import User
from log import get_logger

logger = get_logger('registered_learners')


def delete_registered_learners():
    conn = get_pg_connection()
    sql = "delete from registered_learners"
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()


def insert_registered_learners(users: List[User]):
    conn = get_pg_connection()
    for _i in range(0, len(users), 1000):
        batch = users[_i:_i + 1000]
        logger.info(f"Inserting {len(batch)} records")
        rows = ((
            user.uid,
            user.email,
            user.active,
            user.full_name,
            user.organisational_unit_id,
            user.formatted_org_name,
            user.grade_id,
            user.grade_name,
            user.profession_id,
            user.profession_name,
            user.created_timestamp,
            user.updated_timestamp,
        ) for user in batch)
        sql = f"""
              INSERT INTO registered_learners (uid, email, active, full_name, organisation_id, organisation_name, grade_id, grade_name, profession_id, profession_name, created_timestamp, updated_timestamp)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
              """
        with conn.cursor() as cursor:
            cursor.executemany(sql, rows)
        conn.commit()
