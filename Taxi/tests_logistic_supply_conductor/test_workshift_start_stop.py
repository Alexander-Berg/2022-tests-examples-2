import datetime

import pytest

PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID = 'e2b66c10ece54751a8db96b3a2039b0f'


START_IDEMPOTENCY = '127c2f1c-4471-49f4-b80f-c1c7bb98618b'
STOP_IDEMPOTENCY = 'f124c0e6-ce1c-4376-ae09-30a42e1cf655'


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Timezone': 'Europe/Moscow',
    'X-Remote-IP': '12.34.56.78',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


def check_db_contents(pgsql, expected_db_contents):
    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM logistic_supply_conductor.workshift_slot_subscribers
        ORDER BY id
        """,
    )
    actual_db_contents = list(cursor)

    assert len(actual_db_contents) == len(expected_db_contents)

    for actual_tuple, expected_tuple in zip(
            actual_db_contents, expected_db_contents,
    ):
        actual = list(actual_tuple)
        expected = list(expected_tuple)
        assert len(actual) == len(expected)
        if actual[5] is not None or expected[5] is not None:
            assert abs((actual[5] - expected[5]).total_seconds()) < 1800
            del actual[5:6]
            del expected[5:6]
        if expected[4] is None:
            del actual[4:5]
            del expected[4:5]
        assert abs((actual[3] - expected[3]).total_seconds()) < 1800
        del actual[3:4]
        del expected[3:4]
        assert actual == expected


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
@pytest.mark.parametrize(
    'slot_id, rule_version, response_code, expected_db_contents_after_start,'
    'expected_db_contents_after_stop, expected_audit_contents, expected_tags,'
    'client_events_times_called',
    [
        ('00000000000000000000000000000000', 1, 404, [], [], [], None, 0),
        (
            '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            100,
            404,
            [],
            [],
            [],
            None,
            0,
        ),
        (
            '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            2,
            200,
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    START_IDEMPOTENCY,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    2,
                    None,
                    None,
                    STOP_IDEMPOTENCY,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
                (
                    2,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            ['foo', 'bar', 'baz'],
            1,
        ),
        pytest.param(
            '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            2,
            200,
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    'qux',
                    START_IDEMPOTENCY,
                    datetime.timedelta(seconds=3700),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=100),
                ),
            ],
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    2,
                    None,
                    None,
                    STOP_IDEMPOTENCY,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    'qux',
                    datetime.timedelta(seconds=3700),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=100),
                ),
                (
                    2,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            ['foo', 'bar', 'baz', 'qux'],
            1,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_STATE_TRANSITION_SETTINGS={
                    'default_tag_on_subscription': 'qux',
                    'free_time_extra': 100,
                },
            ),
        ),
        pytest.param(
            '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            2,
            200,
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    START_IDEMPOTENCY,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    2,
                    None,
                    None,
                    STOP_IDEMPOTENCY,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
                (
                    2,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            ['foo', 'bar', 'baz'],
            2,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_NOTIFICATION_SETTINGS={
                    'enabled': True,
                    'ttl': 100,
                    'polygon_color_scheme': {
                        'on_order': {
                            'color_border': {
                                'day': '#DA8400',
                                'night': '#DA8400',
                            },
                            'color_fill': {
                                'day': '#15DA8400',
                                'night': '#15DA8400',
                            },
                        },
                        'default': {
                            'color_border': {
                                'day': '#DA8400',
                                'night': '#DA8400',
                            },
                            'color_fill': {
                                'day': '#15DA8400',
                                'night': '#15DA8400',
                            },
                        },
                    },
                },
            ),
        ),
    ],
)
async def test_workshift_start_stop(
        taxi_logistic_supply_conductor,
        pgsql,
        tags,
        client_events,
        driver_status,
        slot_id,
        rule_version,
        response_code,
        expected_db_contents_after_start,
        expected_db_contents_after_stop,
        expected_audit_contents,
        expected_tags,
        client_events_times_called,
):
    await taxi_logistic_supply_conductor.invalidate_caches()
    tags.set_tags(expected_tags, None)

    response_start = await taxi_logistic_supply_conductor.post(
        'internal/v1/courier/on-workshift-start',
        json={
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': DRIVER_ID,
            },
            'offer_identity': {
                'slot_id': slot_id,
                'rule_version': rule_version,
            },
        },
        headers={**DEFAULT_HEADERS, 'X-Idempotency-Token': START_IDEMPOTENCY},
    )

    assert response_start.status_code == response_code
    check_db_contents(pgsql, expected_db_contents_after_start)

    await taxi_logistic_supply_conductor.invalidate_caches()
    tags.set_tags(None, expected_tags)

    response_stop = await taxi_logistic_supply_conductor.post(
        'internal/v1/courier/on-workshift-stop',
        json={
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': DRIVER_ID,
            },
        },
        headers={**DEFAULT_HEADERS, 'X-Idempotency-Token': STOP_IDEMPOTENCY},
    )

    assert response_stop.status_code == response_code
    check_db_contents(pgsql, expected_db_contents_after_stop)

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM logistic_supply_conductor.workshift_slot_subscribers_audit
        ORDER BY id
        """,
    )
    actual_audit_contents = list(cursor)

    assert len(actual_audit_contents) == len(expected_audit_contents)

    for actual_tuple, expected_tuple in zip(
            actual_audit_contents, expected_audit_contents,
    ):
        actual = list(actual_tuple)
        expected = list(expected_tuple)
        assert len(actual) == len(expected)
        if actual[5] is not None or expected[5] is not None:
            assert abs((actual[5] - expected[5]).total_seconds()) < 1800
            del actual[5:6]
            del expected[5:6]
        assert abs((actual[4] - expected[4]).total_seconds()) < 1800
        del actual[4:5]
        del expected[4:5]
        assert actual == expected

    assert client_events.times_called == client_events_times_called


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
@pytest.mark.parametrize(
    'slot_id, rule_version, response_code, expected_db_contents_after_start,'
    'expected_db_contents_after_stop, expected_audit_contents, expected_tags',
    [
        (
            '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            2,
            200,
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    1,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    START_IDEMPOTENCY,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    2,
                    None,
                    None,
                    STOP_IDEMPOTENCY,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
                (
                    2,
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            ['foo', 'bar', 'baz'],
        ),
    ],
)
async def test_workshift_start_stop_idempotency(
        taxi_logistic_supply_conductor,
        pgsql,
        tags,
        client_events,
        driver_status,
        slot_id,
        rule_version,
        response_code,
        expected_db_contents_after_start,
        expected_db_contents_after_stop,
        expected_audit_contents,
        expected_tags,
):
    await taxi_logistic_supply_conductor.invalidate_caches()
    tags.set_tags(expected_tags, None)

    for _ in range(3):
        response_start = await taxi_logistic_supply_conductor.post(
            'internal/v1/courier/on-workshift-start',
            json={
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'offer_identity': {
                    'slot_id': slot_id,
                    'rule_version': rule_version,
                },
            },
            headers={
                **DEFAULT_HEADERS,
                'X-Idempotency-Token': START_IDEMPOTENCY,
            },
        )

        assert response_start.status_code == response_code
        check_db_contents(pgsql, expected_db_contents_after_start)

    await taxi_logistic_supply_conductor.invalidate_caches()
    tags.set_tags(None, expected_tags)

    for _ in range(3):
        response_stop = await taxi_logistic_supply_conductor.post(
            'internal/v1/courier/on-workshift-stop',
            json={
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
            },
            headers={
                **DEFAULT_HEADERS,
                'X-Idempotency-Token': STOP_IDEMPOTENCY,
            },
        )

        assert response_stop.status_code == response_code
        check_db_contents(pgsql, expected_db_contents_after_stop)

    cursor = pgsql['logistic_supply_conductor'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM logistic_supply_conductor.workshift_slot_subscribers_audit
        ORDER BY id
        """,
    )
    actual_audit_contents = list(cursor)

    assert len(actual_audit_contents) == len(expected_audit_contents)

    for actual_tuple, expected_tuple in zip(
            actual_audit_contents, expected_audit_contents,
    ):
        actual = list(actual_tuple)
        expected = list(expected_tuple)
        assert len(actual) == len(expected)
        if actual[5] is not None or expected[5] is not None:
            assert abs((actual[5] - expected[5]).total_seconds()) < 1800
            del actual[5:6]
            del expected[5:6]
        assert abs((actual[4] - expected[4]).total_seconds()) < 1800
        del actual[4:5]
        del expected[4:5]
        assert actual == expected


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
@pytest.mark.parametrize(
    'slot_id, rule_version, response_code, expected_db_contents_after_start,'
    'expected_db_contents_after_stop, expected_tags',
    [
        (
            '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
            2,
            200,
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    3,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    START_IDEMPOTENCY,
                    datetime.timedelta(seconds=3600),
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            [
                (
                    1,
                    f'({PARK_ID},{DRIVER_ID})',
                    None,
                    datetime.datetime.now(datetime.timezone.utc),
                    None,
                    None,
                    None,
                    STOP_IDEMPOTENCY,
                    None,
                    None,
                    None,
                    None,
                    datetime.timedelta(seconds=0),
                ),
            ],
            ['foo', 'bar', 'baz'],
        ),
    ],
)
async def test_workshift_start_stop_repeat(
        taxi_logistic_supply_conductor,
        pgsql,
        tags,
        client_events,
        driver_status,
        slot_id,
        rule_version,
        response_code,
        expected_db_contents_after_start,
        expected_db_contents_after_stop,
        expected_tags,
):
    for i in range(3):
        await taxi_logistic_supply_conductor.invalidate_caches()
        tags.set_tags(expected_tags, None)

        response_start = await taxi_logistic_supply_conductor.post(
            'internal/v1/courier/on-workshift-start',
            json={
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'offer_identity': {
                    'slot_id': slot_id,
                    'rule_version': rule_version,
                },
            },
            headers={
                **DEFAULT_HEADERS,
                'X-Idempotency-Token': f'{START_IDEMPOTENCY}_{i}',
            },
        )

        assert response_start.status_code == response_code

        expected = list(expected_db_contents_after_start[0])
        expected[7] = f'{START_IDEMPOTENCY}_{i}'
        check_db_contents(pgsql, [tuple(expected)])

        await taxi_logistic_supply_conductor.invalidate_caches()
        tags.set_tags(None, expected_tags)

        response_stop = await taxi_logistic_supply_conductor.post(
            'internal/v1/courier/on-workshift-stop',
            json={
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
            },
            headers={
                **DEFAULT_HEADERS,
                'X-Idempotency-Token': f'{STOP_IDEMPOTENCY}_{i}',
            },
        )

        assert response_stop.status_code == response_code

        expected = list(expected_db_contents_after_stop[0])
        expected[7] = f'{STOP_IDEMPOTENCY}_{i}'
        check_db_contents(pgsql, [tuple(expected)])


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
@pytest.mark.config(
    DRIVER_STATUSES_CACHE_SETTINGS={
        '__default__': {
            'cache_enabled': True,
            'full_update_request_parts_count': 1,
            'last_revision_overlap_sec': 1,
        },
    },
    LOGISTIC_SUPPLY_CONDUCTOR_OFFER_DISPLAY_SETTINGS={
        'show_pause_and_resume_buttons': True,
    },
)
@pytest.mark.parametrize(
    'init_sql, response_code, expected_response',
    [
        (None, 200, {'is_logistic_workshifts_enabled': True}),
        (
            f"""
            INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
            (contractor_id, slot_id, subscribed_at, idempotency)
            VALUES
            ('({PARK_ID},{DRIVER_ID})', 1, CURRENT_TIMESTAMP, 'some');
            """,
            200,
            {
                'active_slot': {
                    'identity': {
                        'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                        'rule_version': 2,
                    },
                    'time_range': {
                        'begin': '2033-04-06T08:00:00+00:00',
                        'end': '2033-04-06T20:00:00+00:00',
                    },
                    'activation_state': 'starting',
                    'allowed_transport_types': [],
                    'quota_id': '00000000-0000-0000-0000-000000000000',
                    'description': {'captions': {}, 'icon': 'waiting'},
                    'actions': [],
                },
                'is_logistic_workshifts_enabled': True,
            },
        ),
        pytest.param(
            f"""
            INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
            (
                contractor_id,
                slot_id,
                subscribed_at,
                free_time_end,
                free_time_extra,
                idempotency
            )
            VALUES
            (
                '({PARK_ID},{DRIVER_ID})',
                1,
                CURRENT_TIMESTAMP - '1 hour'::INTERVAL,
                '2033-04-06T13:00:00+00:00',
                '1 second'::INTERVAL,
                'some'
            );
            """,
            200,
            {
                'active_slot': {
                    'identity': {
                        'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                        'rule_version': 2,
                    },
                    'time_range': {
                        'begin': '2033-04-06T08:00:00+00:00',
                        'end': '2033-04-06T20:00:00+00:00',
                    },
                    'activation_state': 'started',
                    'allowed_transport_types': [],
                    'quota_id': '00000000-0000-0000-0000-000000000000',
                    'description': {'captions': {}, 'icon': 'waiting'},
                    'actions': [],
                    'free_time_end': '2033-04-06T12:59:59+00:00',
                    'extra_time_end': '2033-04-06T13:00:00+00:00',
                },
                'is_logistic_workshifts_enabled': True,
            },
        ),
        (
            f"""
            INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
            (contractor_id, slot_id, subscribed_at, idempotency)
            VALUES
            ('({PARK_ID},{DRIVER_ID})', NULL, NULL, 'some');
            """,
            200,
            {'is_logistic_workshifts_enabled': True},
        ),
        pytest.param(
            None,
            200,
            {'is_logistic_workshifts_enabled': False},
            marks=pytest.mark.config(ENABLE_LOGISTIC_WORKSHIFTS_ON_PRO=False),
        ),
        pytest.param(
            f"""
            INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
            (contractor_id, slot_id, subscribed_at, idempotency)
            VALUES
            ('({PARK_ID},{DRIVER_ID})', 1, CURRENT_TIMESTAMP, 'some');
            """,
            200,
            {
                'active_slot': {
                    'identity': {
                        'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                        'rule_version': 2,
                    },
                    'time_range': {
                        'begin': '2033-04-06T08:00:00+00:00',
                        'end': '2033-04-06T20:00:00+00:00',
                    },
                    'activation_state': 'starting',
                    'allowed_transport_types': [],
                    'quota_id': '00000000-0000-0000-0000-000000000000',
                    'description': {'captions': {}, 'icon': 'waiting'},
                    'actions': [],
                },
                'is_logistic_workshifts_enabled': True,
            },
            marks=pytest.mark.config(ENABLE_LOGISTIC_WORKSHIFTS_ON_PRO=False),
        ),
        pytest.param(
            None,
            200,
            {'is_logistic_workshifts_enabled': True},
            marks=pytest.mark.experiments3(
                filename='allowed_performers_ok.json',
            ),
        ),
        pytest.param(
            None,
            200,
            {'is_logistic_workshifts_enabled': False},
            marks=pytest.mark.experiments3(
                filename='allowed_performers_not_ok.json',
            ),
        ),
    ],
)
async def test_workshift_state(
        taxi_logistic_supply_conductor,
        pgsql,
        init_sql,
        response_code,
        expected_response,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/courier/state',
        json={
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': DRIVER_ID,
            },
        },
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == response_code
    assert response.json() == expected_response
