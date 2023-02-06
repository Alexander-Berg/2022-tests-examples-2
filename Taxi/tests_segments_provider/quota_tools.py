import dataclasses


TAGS_SHIPMENTS = 'tags_shipments'
TAGS_COUNT = 'tags_count'
PASSENGER_TAGS_COUNT = 'passenger_tags_count'
GROCERY_TAGS_COUNT = 'grocery_tags_count'
EATS_TAGS_COUNT = 'eats_tags_count'


DEFAULT_QUOTA_REQUIREMENTS = {
    'tags': [TAGS_SHIPMENTS, TAGS_COUNT],
    'passenger_tags': [TAGS_SHIPMENTS, PASSENGER_TAGS_COUNT],
    'grocery_tags': [TAGS_SHIPMENTS, GROCERY_TAGS_COUNT],
    'eats_tags': [TAGS_SHIPMENTS, EATS_TAGS_COUNT],
}


@dataclasses.dataclass
class Assignment:
    name: str
    value: int


@dataclasses.dataclass
class Usage:
    name: str
    usage: int


def insert_requirements(pgsql, requirements):
    cursor = pgsql['segments_provider'].cursor()

    consumer_names = """','""".join(requirements.keys())
    cursor.execute(
        f"""
        SELECT name, id FROM config.consumers
        WHERE name IN ('{consumer_names}')
        """,
    )

    sql_values = str()
    for row in cursor:
        if row[0] in requirements:
            for requirement in requirements[row[0]]:
                sql_values += str((row[1], requirement)) + ','
    if not sql_values:
        return
    sql_values = sql_values[:-1]
    cursor.execute(
        f"""
        INSERT INTO quota.requirements (consumer_id, quota_name)
        VALUES {sql_values}
        """,
    )


def insert_quotas(pgsql, quotas):
    cursor = pgsql['segments_provider'].cursor()
    sql_values = str()
    for owner, values in quotas.items():
        for name, value in values.items():
            sql_values += str((name, owner, value)) + ','
    if not sql_values:
        return
    sql_values = sql_values[:-1]
    cursor.execute(
        f'INSERT INTO quota.quotas (name, owner, value) VALUES {sql_values}',
    )


def insert_assignments(
        pgsql, shipment_name, consumer_name, owner, assignments,
):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""SELECT id, name FROM quota.quotas WHERE owner = '{owner}'""",
    )
    quota_ids = list(cursor)
    cursor.execute(
        f"""
        SELECT s.id
        FROM config.shipments AS s
        INNER JOIN config.consumers AS c ON s.consumer_id = c.id
        WHERE s.name = '{shipment_name}' AND c.name = '{consumer_name}'
        """,
    )
    shipment_ids = list(cursor)
    sql_values = str()
    for assignment in assignments:
        for quota_id, name in quota_ids:
            if assignment.name != name:
                continue
            for shipment_id in shipment_ids:
                sql_values += str((quota_id, shipment_id[0], assignment.value))
                sql_values += ','

    if not sql_values:
        return
    sql_values = sql_values[:-1]
    cursor.execute(
        f"""
        INSERT INTO quota.assignments (quota_id, shipment_id, assignment)
        VALUES {sql_values}
        """,
    )


def get_assignments(pgsql, shipment_name, consumer_name):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT q.owner, q.name, a.assignment
        FROM quota.assignments AS a
        INNER JOIN quota.quotas AS q ON a.quota_id = q.id
        INNER JOIN config.shipments AS s ON a.shipment_id = s.id
        INNER JOIN config.consumers AS c ON s.consumer_id = c.id
        WHERE s.name = '{shipment_name}' AND c.name = '{consumer_name}'
        ORDER BY q.name
        """,
    )

    assignments = [
        (row[0], Assignment(name=row[1], value=row[2])) for row in cursor
    ]
    result = dict()
    for owner, assignment in assignments:
        if owner in result:
            result[owner].append(assignment)
        else:
            result[owner] = [assignment]

    return result


def update_usage(pgsql):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        UPDATE quota.quotas AS q
        SET usage = inp.usage
        FROM (
          SELECT a.quota_id, SUM(assignment) AS usage
          FROM quota.assignments AS a
          JOIN config.shipments AS s ON a.shipment_id = s.id
          WHERE s.status NOT IN ('disabled', 'disabling')
          GROUP BY a.quota_id
        ) AS inp
        WHERE q.id = inp.quota_id
        """,
    )


def get_usage(pgsql, owner):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT name, usage
        FROM quota.quotas
        WHERE owner = '{owner}'
        ORDER BY name
        """,
    )

    return [Usage(name=row[0], usage=row[1]) for row in cursor]
