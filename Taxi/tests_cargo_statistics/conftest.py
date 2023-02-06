# pylint: disable=redefined-outer-name
import datetime

import psycopg2.extras
import pytest

# pylint: disable=import-error,wildcard-import
from cargo_statistics_plugins import *  # noqa: F403 F401


class EventGroup:
    def __init__(self, config, pgsql):
        self.table = config['table']
        self.primary_key = 'event_id'
        self.timestamp = 'event_time'
        self.fields = config['fields']
        self.cursor = pgsql['cargo_statistics'].cursor(
            cursor_factory=psycopg2.extras.DictCursor,
        )

    def insert_events(self, *events):
        fields = (
            f'{self.primary_key}, {self.timestamp}, '
            f'{",".join(self.fields)}, features, extra_fields'
        )
        self.cursor.execute(
            f'INSERT INTO {self.table} ({fields}) '
            f'SELECT {fields} '
            f'FROM jsonb_populate_recordset(null::{self.table}, %s)',
            (psycopg2.extras.Json(events),),
        )

    def expect_events(self, expected):
        saved = sorted(self.get_events(), key=lambda x: x[self.primary_key])
        expected = sorted(expected, key=lambda x: x[self.primary_key])
        if len(saved) != len(expected):
            assert saved == expected

        for saved_event, expected_event in zip(saved, expected):
            saved_event.pop('event_created_ts')
            for key, val in expected_event.items():
                if isinstance(saved_event[key], datetime.datetime):
                    expected_event[key] = datetime.datetime.strptime(
                        val, '%Y-%m-%dT%H:%M:%S%z',
                    )
        assert saved == expected

    def get_events(self):
        self.cursor.execute(f'SELECT * FROM {self.table}')
        return [dict(x) for x in self.cursor]


@pytest.fixture()
def get_handler_config(load_yaml, testsuite_build_dir):
    config_path = testsuite_build_dir.joinpath('configs/service.yaml')
    config = load_yaml(config_path)['components_manager']['components']

    def wrapped(event_group):
        groups = config['event-processor']['event_groups']
        for group in groups:
            if group['name'] == event_group:
                return group
        raise ValueError(f'no handler for group {event_group} found in config')

    return wrapped


@pytest.fixture()
def get_handler(get_handler_config, pgsql):
    def wrapped(name):
        config = get_handler_config(name)
        return EventGroup(config=config, pgsql=pgsql)

    return wrapped


@pytest.fixture()
def manual_dispatch_orders(get_handler):
    return get_handler('manual-dispatch/orders')


@pytest.fixture()
def cargo_orders_orders(get_handler):
    return get_handler('cargo-orders/orders')


@pytest.fixture()
def cargo_claims_claims(get_handler):
    return get_handler('cargo-claims/claims')


@pytest.fixture()
def cargo_claims_segments(get_handler):
    return get_handler('cargo-claims/segments')


@pytest.fixture()
def cargo_dispatch_segments(get_handler):
    return get_handler('cargo-dispatch/segments')


@pytest.fixture()
def cargo_dispatch_waybills(get_handler):
    return get_handler('cargo-dispatch/waybills')


class Timestamp:

    FORMAT = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self, time):
        self.time = time
        if self.time.tzinfo is None:
            self.time = self.time.replace(tzinfo=datetime.timezone.utc)
        else:
            self.time = self.time.astimezone(datetime.timezone.utc)

    @classmethod
    def fromstring(cls, string):
        return datetime.datetime.strptime(string, cls.FORMAT)

    @property
    def tzinfo(self):
        return self.time.tzinfo

    def diff(self, *args, **kwargs):
        return Timestamp(self.time + datetime.timedelta(*args, **kwargs))

    def epoch(self):
        return self.time.timestamp()

    def string(self):
        return self.time.strftime(self.FORMAT)


@pytest.fixture
def load_events(taxi_cargo_statistics, load_json):
    async def wrapper():
        event_groups = [
            'cargo-claims/claims',
            'cargo-claims/segments',
            'cargo-dispatch/segments',
            'cargo-dispatch/waybills',
            'cargo-dispatch/waybill-segments',
            'cargo-orders/orders',
        ]

        for event_group in event_groups:
            json_path = f'events/{event_group}.json'
            events = load_json(json_path)
            response = await taxi_cargo_statistics.post(
                '/v1/events/push',
                params={'event_group': event_group},
                json={'events': events},
            )
            assert response.status_code == 200

    return wrapper
