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
          select count(*)
          from csrs.civil_servant cs
                   join csrs.`identity` csi on cs.identity_id = csi.id
                   join `identity`.`identity` i on csi.uid = i.uid
                   join `identity`.invite inv on inv.for_email = i.email
                   join csrs.grade g on cs.grade_id = g.id
                   join csrs.profession p on cs.profession_id = p.id
          """
    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        return int(cursor.fetchone()[0])


def get_user_details(page: int):
    offset = (page - 1) * PAGE_SIZE
    sql = f"""
        select i.uid, i.email, i.active, cs.full_name, cs.organisational_unit_id, ou.name, cs.grade_id,
        g.name, cs.profession_id, p.name,
        case
            when MAX(inv.accepted_at) is null then max(inv.invited_at)
            else LEAST(MAX(inv.accepted_at), max(inv.invited_at))
        end as 'created_timestamp'
        from csrs.civil_servant cs 
        join csrs.`identity` csi on cs.identity_id = csi.id
        join `identity`.`identity` i on csi.uid = i.uid
        join `identity`.invite inv on inv.for_email = i.email
        join csrs.grade g on cs.grade_id = g.id
        join csrs.profession p on cs.profession_id = p.id
        join (
            select ou.id, organisational_unit.name
            from csrs.organisational_unit ou
            left outer join (
                select ou.id as _id,
                concat(
                        case
                            when grandparent.name is null then ''
                            else concat(grandparent.name, ' | ')
                        end
                    ,
                        case
                            when parent.name is null then ''
                            else concat(parent.name, ' | ')
                        end
                    ,
                        ou.name) as 'name'
                 from csrs.organisational_unit ou
                  left outer join csrs.organisational_unit parent on ou.parent_id = parent.id
                  left outer join csrs.organisational_unit grandparent on parent.parent_id = grandparent.id
                  ) as organisational_unit on organisational_unit._id = ou.id
            ) as ou on cs.organisational_unit_id = ou.id
        group by i.uid
        limit {PAGE_SIZE} offset {offset};
    """
    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        return [
            User(row[0], row[1], bool(row[2]), row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[10])
            for row in
            cursor.fetchall()]
