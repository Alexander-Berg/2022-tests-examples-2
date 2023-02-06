# pylint: disable=redefined-outer-name
import datetime

import pytest


@pytest.fixture()
def get_job_config(load_yaml, testsuite_build_dir):
    config_path = testsuite_build_dir.joinpath('configs/service.yaml')
    config = load_yaml(config_path)

    def wrapped(job_name):
        return config['components_manager']['components'][job_name]

    return wrapped


def _get_config(jobs):
    default_config = {
        'enabled': False,
        'period': 5,
        'period_tolerance': 5,
        'max_delay': 1800,
    }
    enabled_config = {
        'enabled': True,
        'period': 5,
        'period_tolerance': 5,
        'max_delay': 300,
    }
    return {'__default__': default_config, **{k: enabled_config for k in jobs}}


@pytest.fixture(name='mock_cargo_statistics')
def mock_cargo_statistics(mockserver):
    def compare_events(request, expected):
        request = sorted(request, key=lambda x: x['event_id'])
        expected = sorted(expected, key=lambda x: x['event_id'])
        if len(request) != len(expected):
            assert request == expected

        for req_event, expected_event in zip(request, expected):
            for key, val in req_event.items():
                if key not in expected_event:
                    assert request == expected

                if isinstance(expected_event[key], datetime.datetime):
                    req_event[key] = datetime.datetime.strptime(
                        val, '%Y-%m-%dT%H:%M:%S.%f%z',
                    )
        assert request == expected

    @mockserver.json_handler('/cargo-statistics/v1/events/push')
    def _mock_push(request):
        if context.event_group is not None:
            assert request.query['event_group'] == context.event_group
        if context.events_push.expected_events is not None:
            compare_events(
                request.json['events'], context.events_push.expected_events,
            )

        context.events_push.last_request = request.json
        return {}

    @mockserver.json_handler('/cargo-statistics/v1/events/last-timestamp')
    def _mock_last_ts(request):
        if context.event_group is not None:
            assert request.query['event_group'] == context.event_group
        return {'last_timestamp': context.last_timestamp.last_timestamp}

    class EventsPushContext:
        def __init__(self):
            self.handler = _mock_push
            self.last_request = None
            self.expected_events = None

    class LastTimestampContext:
        def __init__(self):
            self.handler = _mock_last_ts
            self.last_timestamp = '2020-01-01T00:00:00+00:00'

    class Context:
        def __init__(self):
            self.event_group = None
            self.events_push = EventsPushContext()
            self.last_timestamp = LastTimestampContext()

    context = Context()
    return context


@pytest.fixture(name='get_pg_events')
def get_pg_events(pgsql, get_job_config):
    def make_fields(fields):
        return ','.join(
            '{} AS {}'.format(x.get('select_as', x['name']), x['name'])
            for x in fields
        )

    def make_fields_json(fields):
        joined = ','.join(
            '\'{}\', {}'.format(x['name'], x.get('select_as', x['name']))
            for x in fields
        )
        return f'json_build_object({joined})'

    def wrapped(job_name, since=None):
        config = get_job_config(job_name)
        database = config['cluster'][config['cluster'].find('-') + 1 :]
        since = since or datetime.datetime(1970, 1, 1, 0, 0, 0)
        cursor = pgsql[database].dict_cursor()
        names = config['pg_stats_table']
        cursor.execute(
            f"""
            SELECT {names['primary_key']} AS event_id,
                   {names['timestamp']} AS event_time,
                   {make_fields(names['fields'])},
                   {make_fields_json(names['features'])} AS features,
                   {make_fields_json(names['extra_fields'])} AS extra_fields
            FROM {names['name']} t
            WHERE {names['timestamp']} > %s
            """,
            (since,),
        )
        return [dict(x) for x in cursor]

    return wrapped


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'cargo_statistics(jobs): mark to enable cargo-statistics jobs',
    )


def pytest_runtest_setup(item):
    marker = item.get_closest_marker('cargo_statistics')
    if marker is None:
        return
    job, event_group = marker.args
    kwargs = marker.kwargs
    item.add_marker(
        pytest.mark.config(
            CARGO_STATISTICS_JOBS_SETTINGS=_get_config([event_group]),
        ),
    )
    if kwargs.get('disable_jobs', True):
        # keeping it enabled might cause flaps
        # for some reason this also disables (some) other periodic tasks
        item.add_marker(pytest.mark.suspend_periodic_tasks(job + '-periodic'))
