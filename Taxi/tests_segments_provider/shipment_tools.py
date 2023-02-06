import dataclasses
import datetime as dt
import enum
import json
from typing import Dict
from typing import List
from typing import Optional


class UnitOfTime(enum.Enum):
    SECONDS = 'seconds'
    MINUTES = 'minutes'
    HOURS = 'hours'


@dataclasses.dataclass
class Schedule:
    start_at: dt.datetime
    unit: UnitOfTime
    count: int


class YqlSyntax(enum.Enum):
    SQLv1 = 'SQLv1'
    CLICKHOUSE = 'CLICKHOUSE'


@dataclasses.dataclass
class YqlQuery:
    syntax: YqlSyntax
    query: str


@dataclasses.dataclass
class TagsConsumerSettings:
    allowed_tag_names: List[str]
    entity_type: Optional[str] = None


@dataclasses.dataclass
class Quotas:
    owner: str
    assignments: Dict[str, int]


@dataclasses.dataclass
class Shipment:
    name: str
    ticket: str
    maintainers: List[str]
    is_enabled: bool
    labels: List[str]
    schedule: Schedule
    source: YqlQuery
    consumer: TagsConsumerSettings
    quotas: Optional[Quotas] = None

    def as_request_data(self):
        result = {
            'name': self.name,
            'ticket': self.ticket,
            'is_enabled': self.is_enabled,
            'labels': [{'name': label} for label in self.labels],
            'maintainers': [{'login': login} for login in self.maintainers],
            'schedule': {
                'type': 'periodic',
                'start_at': self.schedule.start_at.isoformat(),
                'period': {
                    'unit': self.schedule.unit.value,
                    'count': self.schedule.count,
                },
            },
            'source': {
                'syntax': self.source.syntax.value,
                'query': self.source.query,
            },
            'consumer': {'allowed_tag_names': self.consumer.allowed_tag_names},
        }

        if self.consumer.entity_type:
            result['consumer']['entity_type'] = self.consumer.entity_type
        if self.quotas:
            result['quotas'] = {}
            result['quotas']['owner'] = self.quotas.owner
            result['quotas']['assignments'] = [
                {'name': name, 'value': value}
                for name, value in self.quotas.assignments.items()
            ]

        return result


class Status(enum.Enum):
    NEW = 'new'
    READY = 'ready'
    RUNNING = 'running'
    DISABLING = 'disabling'
    DISABLED = 'disabled'


def _calculate_period(schedule: Schedule) -> dt.timedelta:
    if schedule.unit == UnitOfTime.HOURS:
        seconds_multiplier = 3600
    if schedule.unit == UnitOfTime.MINUTES:
        seconds_multiplier = 60
    if schedule.unit == UnitOfTime.SECONDS:
        seconds_multiplier = 1
    return dt.timedelta(seconds=schedule.count * seconds_multiplier)


@dataclasses.dataclass
class DbShipment:
    name: str
    ticket: str
    maintainers: List[str]
    is_enabled: bool
    labels: List[str]
    schedule: Schedule
    source: YqlQuery
    consumer: TagsConsumerSettings
    created_at: dt.datetime
    updated_at: dt.datetime
    status: Status
    last_modifier: Optional[str] = None
    disable_at: Optional[dt.datetime] = None
    launch_period: Optional[dt.timedelta] = None
    is_relaunch_requested: bool = False

    @staticmethod
    def from_api_shipment(
            shipment: Shipment,
            created_at: dt.datetime,
            updated_at: dt.datetime,
            last_modifier: str,
            timezone: Optional[dt.tzinfo] = None,
            status: Status = Status.READY,
            launch_period: Optional[dt.timedelta] = None,
    ):
        if timezone:
            actual_created_at = created_at.astimezone(timezone)
            actual_updated_at = updated_at.astimezone(timezone)
            actual_start_at = shipment.schedule.start_at.astimezone(timezone)
        else:
            actual_created_at = created_at
            actual_updated_at = updated_at
            actual_start_at = shipment.schedule.start_at

        result = DbShipment(
            name=shipment.name,
            ticket=shipment.ticket,
            maintainers=shipment.maintainers,
            is_enabled=shipment.is_enabled,
            labels=shipment.labels,
            schedule=shipment.schedule,
            source=shipment.source,
            consumer=shipment.consumer,
            created_at=actual_created_at,
            updated_at=actual_updated_at,
            status=status,
            last_modifier=last_modifier,
            launch_period=(
                launch_period or _calculate_period(shipment.schedule)
            ),
        )
        result.schedule.start_at = actual_start_at
        return result


def get_shipment_insert_query(
        consumer_name: str,
        shipment: DbShipment,
        tag_provider_name_override: Optional[str] = None,
):
    tag_provider_name = (
        tag_provider_name_override
        if tag_provider_name_override
        else 'seagull_' + shipment.name
    )
    strings_delimiter = '\',\''
    allowed_tag_names = (
        'ARRAY[\''
        + strings_delimiter.join(shipment.consumer.allowed_tag_names)
        + '\']'
    )
    entity_type = (
        f'\'{shipment.consumer.entity_type}\''
        if shipment.consumer.entity_type
        else 'null'
    )
    created_at = shipment.created_at.isoformat()
    updated_at = shipment.updated_at.isoformat()
    disable_at = (
        f'\'{shipment.disable_at.isoformat()}\''
        if shipment.disable_at
        else 'null'
    )
    schedule = json.dumps(
        {
            'type': 'periodic',
            'start_at': shipment.schedule.start_at.isoformat(),
            'period': {
                'unit': shipment.schedule.unit.value,
                'count': shipment.schedule.count,
            },
        },
    )

    users_to_insert = set()

    if shipment.maintainers:
        maintainers = (
            f'ARRAY[\'{strings_delimiter.join(shipment.maintainers)}\']'
        )
        users_to_insert.update(shipment.maintainers)
    else:
        maintainers = '\'{}\'::text[]'

    if shipment.labels:
        labels = f'ARRAY[\'{strings_delimiter.join(shipment.labels)}\']'
    else:
        labels = '\'{}\'::text[]'

    launch_period = (
        f'\'{shipment.launch_period.total_seconds()} seconds\''
        if shipment.launch_period
        else 'null'
    )

    if shipment.last_modifier:
        last_modifier = f'\'{shipment.last_modifier}\''
        users_to_insert.add(shipment.last_modifier)
    else:
        last_modifier = 'null'

    users = f'ARRAY[\'{strings_delimiter.join(users_to_insert)}\']'

    def escape(raw_string: str):
        return raw_string.replace('\\', '\\').replace('\'', '\'\'')

    query = f"""
        WITH insert_consumer AS (
            INSERT INTO config.consumers (name)
            VALUES ('{consumer_name}')
            ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name
            RETURNING id
        ), insert_tags_provider AS (
            INSERT INTO config.tags_providers
                (consumer_id, name, allowed_tag_names, entity_type)
            VALUES ((SELECT id FROM insert_consumer), '{tag_provider_name}',
                {allowed_tag_names}, {entity_type})
            RETURNING id
        ),  insert_yql AS (
            INSERT INTO config.yql_queries (syntax, query)
            VALUES ('{shipment.source.syntax.value}',
                '{escape(shipment.source.query)}')
            RETURNING id
        ), insert_users AS (
            INSERT INTO config.users (login)
            SELECT UNNEST({users})
            ON CONFLICT (login) DO UPDATE SET login = excluded.login
            RETURNING id, login
        ), insert_shipment AS (
            INSERT INTO config.shipments (consumer_id, name, ticket,
                created_at, updated_at, schedule, yql_query_id,
                tag_provider_id, is_enabled, status, last_modifier_user_id,
                disable_at, launch_period)
            VALUES ((SELECT id FROM insert_consumer), '{shipment.name}',
                '{shipment.ticket}', '{created_at}', '{updated_at}',
                '{schedule}'::jsonb, (SELECT id FROM insert_yql),
                (SELECT id FROM insert_tags_provider), {shipment.is_enabled},
                '{shipment.status.value}',
                (SELECT id FROM insert_users WHERE login = {last_modifier}),
                {disable_at}, {launch_period})
            RETURNING id
        ), insert_maintainers AS (
            INSERT INTO config.maintainers (shipment_id, user_id)
            SELECT (SELECT id FROM insert_shipment), id
            FROM insert_users
            WHERE login = ANY({maintainers})
        ), insert_labels AS (
            INSERT INTO config.labels (name)
            SELECT UNNEST({labels})
            ON CONFLICT (name) DO UPDATE SET name = excluded.name
            RETURNING id
        ), insert_label_relations AS (
            INSERT INTO config.shipment_label_relations (shipment_id, label_id)
            SELECT (SELECT id from insert_shipment), id
            FROM insert_labels
        )
        SELECT id from insert_shipment
    """
    return query


def insert_shipment(
        pgsql,
        consumer_name: str,
        shipment: DbShipment,
        tag_provider_name_override: Optional[str] = None,
):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        get_shipment_insert_query(
            consumer_name, shipment, tag_provider_name_override,
        ),
    )


def find_shipment(pgsql, consumer: str, name: str):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT shipments.name,
            shipments.ticket,
            coalesce((
                SELECT array_agg(users.login ORDER BY users.login)
                FROM config.users
                        JOIN config.maintainers
                            ON users.id = maintainers.user_id
                WHERE maintainers.shipment_id = shipments.id),
                '{{}}'::text[]) AS maintainers,
            shipments.is_enabled,
            coalesce((
                SELECT array_agg(labels.name ORDER BY labels.name)
                FROM config.labels
                        JOIN config.shipment_label_relations rel
                            ON labels.id = rel.label_id
                WHERE rel.shipment_id = shipments.id), '{{}}'::text[]) labels,
            shipments.schedule,
            tags_providers.name AS provider_name,
            tags_providers.allowed_tag_names,
            tags_providers.entity_type,
            yql_queries.syntax,
            yql_queries.query,
            shipments.created_at,
            shipments.updated_at,
            shipments.status,
            coalesce((
                SELECT login
                FROM config.users
                WHERE id = shipments.last_modifier_user_id),
                'unknown') AS last_modifier,
            shipments.disable_at,
            shipments.launch_period,
            shipments.is_relaunch_requested
        FROM config.shipments
                JOIN config.consumers
                    ON shipments.consumer_id = consumers.id
                JOIN config.tags_providers
                    ON shipments.tag_provider_id = tags_providers.id
                JOIN config.yql_queries
                    ON shipments.yql_query_id = yql_queries.id
        WHERE consumers.name = '{consumer}'
        AND shipments.name = '{name}'
        """,
    )
    rows = list(row for row in cursor)
    assert len(rows) == 1
    for row in rows:
        db_schedule = row[5]

        return DbShipment(
            name=row[0],
            ticket=row[1],
            maintainers=row[2],
            is_enabled=row[3],
            labels=row[4],
            schedule=Schedule(
                start_at=dt.datetime.fromisoformat(db_schedule['start_at']),
                unit=UnitOfTime(db_schedule['period']['unit']),
                count=db_schedule['period']['count'],
            ),
            consumer=TagsConsumerSettings(
                allowed_tag_names=row[7], entity_type=row[8],
            ),
            source=YqlQuery(syntax=YqlSyntax(row[9]), query=row[10]),
            created_at=row[11],
            updated_at=row[12],
            status=Status(row[13]),
            last_modifier=row[14],
            disable_at=row[15],
            launch_period=row[16],
            is_relaunch_requested=row[17],
        )


def get_consumer_insert_query(name: str):
    return f'INSERT INTO config.consumers (name) VALUES (\'{name}\')'


def get_update_yql_query(
        consumer_name: str, shipment_name: str, query: YqlQuery,
):
    def escape(raw_string: str):
        return raw_string.replace('\\', '\\').replace('\'', '\'\'')

    return f"""
        WITH yql_query AS (
            SELECT shipments.yql_query_id
            FROM config.shipments
            JOIN config.consumers
                ON shipments.consumer_id = consumers.id
            WHERE consumers.name = '{consumer_name}'
              AND shipments.name = '{shipment_name}'
        )
        UPDATE config.yql_queries
        SET query = '{escape(query.query)}',
            syntax = '{query.syntax.value}'
        WHERE id = (SELECT yql_query_id FROM yql_query)
    """
