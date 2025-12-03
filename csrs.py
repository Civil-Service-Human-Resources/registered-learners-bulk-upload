import math
from datetime import datetime

from config import get_mysql_connection, PAGE_SIZE
from log import get_logger

logger = get_logger("csrs")


class User:
    def __init__(self, uid: str, email: str, active: bool, full_name: str, organisational_unit_id: int,
                 formatted_org_name: str, grade_id: str, grade_name: str, profession_id: int, profession_name: str,
                 created_timestamp: datetime, updated_timestamp: datetime):
        self.uid = uid
        self.email = email
        self.active = active
        self.full_name = full_name
        self.organisational_unit_id = organisational_unit_id
        self.formatted_org_name = formatted_org_name
        self.grade_id = grade_id
        self.grade_name = grade_name
        self.profession_id = profession_id
        self.profession_name = profession_name
        self.created_timestamp = created_timestamp
        self.updated_timestamp = updated_timestamp


def get_all_users():
    users = []
    count = count_users()
    logger.info(f"Found {count} total registered users")
    pages = math.ceil(count / PAGE_SIZE)
    logger.info(f"Found {pages} pages (total: {count} / max page size: {PAGE_SIZE})")
    for page in range(pages):
        page = page + 1
        logger.info(f"Processing page {page}")
        users.extend(get_user_details(page))
    return users


def count_users():
    sql = """
          WITH result_set AS (
               SELECT DISTINCT i.email
               FROM identity.identity i
                        LEFT JOIN csrs.identity ci ON ci.uid = i.uid
                        LEFT JOIN csrs.civil_servant csrv ON csrv.identity_id = ci.id
               WHERE csrv.full_name IS NOT NULL
          )
          SELECT COUNT(*) AS total_count
          FROM result_set
          """
    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        return int(cursor.fetchone()[0])


def get_user_details(page: int):
    offset = (page - 1) * PAGE_SIZE
    sql = f"""
            WITH RECURSIVE org_hierarchy AS (
                SELECT
                    cs.id AS civil_servant_id,
                    ou.id AS org_id,
                    ou.parent_id,
                    ou.name,
                    1 AS level_order
                FROM csrs.civil_servant cs
                LEFT JOIN csrs.organisational_unit ou ON cs.organisational_unit_id = ou.id
                UNION ALL
                SELECT
                    oh.civil_servant_id,
                    ou.id,
                    ou.parent_id,
                    ou.name,
                    oh.level_order + 1
                FROM org_hierarchy oh
                JOIN csrs.organisational_unit ou ON oh.parent_id = ou.id
                WHERE oh.parent_id IS NOT NULL
            ),
            emailupd AS (
                SELECT
                    new_email AS email,
                    MAX(updated_at)   AS max_updated,
                    MAX(requested_at) AS max_requested
                FROM identity.email_update
                WHERE email_update_status = 'UPDATED'
                GROUP BY new_email
            )
            SELECT
                i.uid,
                i.email,
                i.active,
                cs.full_name,
                cs.organisational_unit_id,
                GROUP_CONCAT(oh.name ORDER BY oh.level_order DESC SEPARATOR ' | ') AS organisational_unit_name,
                cs.grade_id,
                g.name AS grade_name,
                cs.profession_id,
                p.name AS profession_name,
                CASE
                    WHEN max_invited IS NULL AND max_accepted IS NULL THEN
                        CASE
                            WHEN eu.email IS NOT NULL THEN
                                CASE
                                    WHEN eu.max_updated IS NOT NULL THEN eu.max_updated
                                    WHEN eu.max_requested IS NOT NULL THEN eu.max_requested
                                    ELSE '2000-01-01 00:00:00.000'
                                END
                            ELSE '2000-01-01 00:00:00.000'
                        END
                    WHEN max_accepted IS NULL THEN max_invited
                    ELSE LEAST(max_accepted, max_invited)
                END AS created_timestamp
            FROM csrs.civil_servant cs
            LEFT JOIN csrs.identity ci     ON cs.identity_id = ci.id
            LEFT JOIN identity.identity i  ON ci.uid = i.uid
            LEFT JOIN (
                SELECT for_email,
                    MAX(accepted_at) AS max_accepted,
                    MAX(invited_at)  AS max_invited
                FROM identity.invite
                GROUP BY for_email
            ) inv ON inv.for_email = i.email
            LEFT JOIN emailupd eu          ON eu.email = i.email
            LEFT JOIN org_hierarchy oh     ON oh.civil_servant_id = cs.id
            LEFT JOIN csrs.grade g         ON cs.grade_id = g.id
            LEFT JOIN csrs.profession p    ON cs.profession_id = p.id
            WHERE cs.full_name IS NOT NULL AND i.email IS NOT NULL
            GROUP BY i.uid
            ORDER BY created_timestamp ASC
        limit {PAGE_SIZE} offset {offset};
    """
    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        return [
            User(row[0], row[1], bool(row[2]), row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[10])
            for row in
            cursor.fetchall()]
