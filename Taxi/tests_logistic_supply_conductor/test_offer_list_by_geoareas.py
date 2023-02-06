import pytest

PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID_1 = 'e2b66c10ece54751a8db96b3a2039b0f'
DRIVER_ID_2 = '40295b99f56a46f1b309d940715a15dd'


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Timezone': 'Asia/Yekaterinburg',
    'X-Remote-IP': '12.34.56.78',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


DEFAULT_VEWPORT = {
    'top_left': {'lat': 63.5, 'lon': 52.5},
    'bottom_right': {'lat': 62.5, 'lon': 53.5},
}


@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID_1}', 'foo1'),
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID_1}', 'bar2'),
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID_2}', 'foo1'),
    ],
)
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_courier_requirements_with_exams.sql',
        'pg_descriptive_items_for_offers.sql',
    ],
)
@pytest.mark.parametrize(
    'init_sql, add_new_slot, viewport, driver_id,'
    'exams, exams_times_called, expected_response',
    [
        ([], False, DEFAULT_VEWPORT, DRIVER_ID_1, None, 0, {'geoareas': []}),
        (
            [
                """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            ],
            False,
            DEFAULT_VEWPORT,
            DRIVER_ID_1,
            None,
            0,
            {
                'geoareas': [
                    {
                        'display_features': {'pin_size': 'big'},
                        'offers': [
                            {
                                'identity': {
                                    'rule_version': 2,
                                    'slot_id': (
                                        '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                    ),
                                },
                                'item_view': {
                                    'captions': {'title': '13:00—01:00'},
                                    'icon': 'waiting',
                                },
                                'activation_state': 'waiting',
                                'allowed_transport_types': [
                                    'pedestrian',
                                    'auto',
                                    'bicycle',
                                ],
                                'cancellation_opportunity': {
                                    'offer': {
                                        'fine_value': {
                                            'currency_code': 'RUB',
                                            'value': '0',
                                        },
                                    },
                                },
                                'description': {
                                    'captions': {
                                        'title': 'The Second Geoarea',
                                        'subtitle': 'Slot is planned',
                                    },
                                    'icon': 'waiting',
                                    'items': [
                                        {
                                            'title': 'Schedule',
                                            'content_code_hint': 'default',
                                            'value': '13:00—01:00',
                                        },
                                        {'content_code_hint': 'capacity'},
                                        {
                                            'text': 'Localized subtitle',
                                            'title': 'Localized title',
                                            'content_code_hint': 'default',
                                            'value': '42',
                                        },
                                        {
                                            'title': 'Free time limit',
                                            'text': 'for toilet and rest',
                                            'content_code_hint': 'default',
                                            'value': '60:00',
                                        },
                                    ],
                                },
                                'requirements': [
                                    {
                                        'is_satisfied': True,
                                        'items': [
                                            {
                                                'captions': {
                                                    'title': 'Lorem ipsum',
                                                    'subtitle': (
                                                        'Dolor sit\namet'
                                                    ),
                                                },
                                                'icon': 'check_failed',
                                                'is_satisfied': False,
                                            },
                                            {
                                                'captions': {
                                                    'title': 'Consectetur',
                                                    'subtitle': '',
                                                },
                                                'icon': 'check_ok',
                                                'is_satisfied': True,
                                            },
                                        ],
                                    },
                                ],
                                'time_range': {
                                    'begin': '2033-04-06T08:00:00+00:00',
                                    'end': '2033-04-06T20:00:00+00:00',
                                },
                                'quota_id': (
                                    'af31c824-066d-46df-0001-100000000001'
                                ),
                                'visibility_info': {},
                            },
                        ],
                        'pin_point': {'lat': 63.0, 'lon': 53.0},
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                        'title': 'The Second Geoarea',
                    },
                ],
            },
        ),
        (
            [
                """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            ],
            False,
            DEFAULT_VEWPORT,
            DRIVER_ID_2,
            {
                'exams': [
                    {
                        'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID_2}',
                        'data': [],
                    },
                ],
            },
            1,
            {
                'geoareas': [
                    {
                        'display_features': {'pin_size': 'big'},
                        'offers': [
                            {
                                'identity': {
                                    'rule_version': 2,
                                    'slot_id': (
                                        '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                    ),
                                },
                                'time_range': {
                                    'begin': '2033-04-06T08:00:00+00:00',
                                    'end': '2033-04-06T20:00:00+00:00',
                                },
                                'quota_id': (
                                    'af31c824-066d-46df-0001-100000000001'
                                ),
                                'visibility_info': {
                                    'invisibility_audit_reasons': [
                                        'None of requirements matched: bar',
                                    ],
                                },
                            },
                        ],
                        'pin_point': {'lat': 63.0, 'lon': 53.0},
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                        'title': 'The Second Geoarea',
                    },
                ],
            },
        ),
        (
            [
                """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            ],
            False,
            DEFAULT_VEWPORT,
            DRIVER_ID_2,
            {
                'exams': [
                    {
                        'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID_2}',
                        'data': [{'course': 'cool_dude', 'result': 3}],
                    },
                ],
            },
            1,
            {
                'geoareas': [
                    {
                        'display_features': {'pin_size': 'big'},
                        'offers': [
                            {
                                'identity': {
                                    'rule_version': 2,
                                    'slot_id': (
                                        '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                    ),
                                },
                                'time_range': {
                                    'begin': '2033-04-06T08:00:00+00:00',
                                    'end': '2033-04-06T20:00:00+00:00',
                                },
                                'quota_id': (
                                    'af31c824-066d-46df-0001-100000000001'
                                ),
                                'visibility_info': {
                                    'invisibility_audit_reasons': [
                                        'None of requirements matched: bar',
                                    ],
                                },
                            },
                        ],
                        'pin_point': {'lat': 63.0, 'lon': 53.0},
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                        'title': 'The Second Geoarea',
                    },
                ],
            },
        ),
        (
            [
                """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            ],
            False,
            DEFAULT_VEWPORT,
            DRIVER_ID_2,
            {
                'exams': [
                    {
                        'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID_2}',
                        'data': [{'course': 'cool_dude', 'result': 4}],
                    },
                ],
            },
            1,
            {
                'geoareas': [
                    {
                        'display_features': {'pin_size': 'big'},
                        'offers': [
                            {
                                'identity': {
                                    'rule_version': 2,
                                    'slot_id': (
                                        '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                    ),
                                },
                                'item_view': {
                                    'captions': {'title': '13:00—01:00'},
                                    'icon': 'waiting',
                                },
                                'activation_state': 'waiting',
                                'allowed_transport_types': [
                                    'pedestrian',
                                    'auto',
                                    'bicycle',
                                ],
                                'cancellation_opportunity': {
                                    'offer': {
                                        'fine_value': {
                                            'currency_code': 'RUB',
                                            'value': '0',
                                        },
                                    },
                                },
                                'description': {
                                    'captions': {
                                        'title': 'The Second Geoarea',
                                        'subtitle': 'Slot is planned',
                                    },
                                    'icon': 'waiting',
                                    'items': [
                                        {
                                            'title': 'Schedule',
                                            'content_code_hint': 'default',
                                            'value': '13:00—01:00',
                                        },
                                        {'content_code_hint': 'capacity'},
                                        {
                                            'text': 'Localized subtitle',
                                            'title': 'Localized title',
                                            'content_code_hint': 'default',
                                            'value': '42',
                                        },
                                        {
                                            'title': 'Free time limit',
                                            'text': 'for toilet and rest',
                                            'content_code_hint': 'default',
                                            'value': '60:00',
                                        },
                                    ],
                                },
                                'requirements': [
                                    {
                                        'is_satisfied': True,
                                        'items': [
                                            {
                                                'captions': {
                                                    'title': 'Lorem ipsum',
                                                    'subtitle': (
                                                        'Dolor sit\namet'
                                                    ),
                                                },
                                                'icon': 'check_failed',
                                                'is_satisfied': False,
                                            },
                                            {
                                                'captions': {
                                                    'title': 'Consectetur',
                                                    'subtitle': '',
                                                },
                                                'icon': 'check_ok',
                                                'is_satisfied': True,
                                            },
                                        ],
                                    },
                                ],
                                'time_range': {
                                    'begin': '2033-04-06T08:00:00+00:00',
                                    'end': '2033-04-06T20:00:00+00:00',
                                },
                                'quota_id': (
                                    'af31c824-066d-46df-0001-100000000001'
                                ),
                                'visibility_info': {},
                            },
                        ],
                        'pin_point': {'lat': 63.0, 'lon': 53.0},
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                        'title': 'The Second Geoarea',
                    },
                ],
            },
        ),
        (
            [
                """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            ],
            True,
            DEFAULT_VEWPORT,
            DRIVER_ID_1,
            None,
            0,
            {
                'geoareas': [
                    {
                        'display_features': {'pin_size': 'big'},
                        'offers': [
                            {
                                'identity': {
                                    'rule_version': 2,
                                    'slot_id': (
                                        '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                    ),
                                },
                                'item_view': {
                                    'captions': {'title': '13:00—01:00'},
                                    'icon': 'waiting',
                                },
                                'activation_state': 'waiting',
                                'allowed_transport_types': [
                                    'pedestrian',
                                    'auto',
                                    'bicycle',
                                ],
                                'cancellation_opportunity': {
                                    'offer': {
                                        'fine_value': {
                                            'currency_code': 'RUB',
                                            'value': '0',
                                        },
                                    },
                                },
                                'description': {
                                    'captions': {
                                        'title': 'The Second Geoarea',
                                        'subtitle': 'Slot is planned',
                                    },
                                    'icon': 'waiting',
                                    'items': [
                                        {
                                            'title': 'Schedule',
                                            'content_code_hint': 'default',
                                            'value': '13:00—01:00',
                                        },
                                        {'content_code_hint': 'capacity'},
                                        {
                                            'text': 'Localized subtitle',
                                            'title': 'Localized title',
                                            'content_code_hint': 'default',
                                            'value': '42',
                                        },
                                        {
                                            'title': 'Free time limit',
                                            'text': 'for toilet and rest',
                                            'content_code_hint': 'default',
                                            'value': '60:00',
                                        },
                                    ],
                                },
                                'requirements': [
                                    {
                                        'is_satisfied': True,
                                        'items': [
                                            {
                                                'captions': {
                                                    'title': 'Lorem ipsum',
                                                    'subtitle': (
                                                        'Dolor sit\namet'
                                                    ),
                                                },
                                                'icon': 'check_failed',
                                                'is_satisfied': False,
                                            },
                                            {
                                                'captions': {
                                                    'title': 'Consectetur',
                                                    'subtitle': '',
                                                },
                                                'icon': 'check_ok',
                                                'is_satisfied': True,
                                            },
                                        ],
                                    },
                                ],
                                'time_range': {
                                    'begin': '2033-04-06T08:00:00+00:00',
                                    'end': '2033-04-06T20:00:00+00:00',
                                },
                                'quota_id': (
                                    'af31c824-066d-46df-0001-100000000001'
                                ),
                                'visibility_info': {},
                            },
                            {
                                'identity': {
                                    'rule_version': 2,
                                    'slot_id': (
                                        '76a3176e-f759-44bc-8fc7-43ea091bd68c'
                                    ),
                                },
                                'item_view': {
                                    'captions': {
                                        'title': '14:00—02:00',
                                        'subtitle': 'Slot is cancelled',
                                    },
                                    'icon': 'cancelled',
                                },
                                'activation_state': 'cancelled',
                                'allowed_transport_types': [
                                    'pedestrian',
                                    'auto',
                                    'bicycle',
                                ],
                                'cancellation_opportunity': {
                                    'offer': {
                                        'fine_value': {
                                            'currency_code': 'RUB',
                                            'value': '0',
                                        },
                                    },
                                },
                                'description': {
                                    'captions': {
                                        'title': 'The Second Geoarea',
                                        'subtitle': 'Slot is cancelled',
                                    },
                                    'icon': 'cancelled',
                                    'items': [
                                        {
                                            'title': 'Schedule',
                                            'content_code_hint': 'default',
                                            'value': '14:00—02:00',
                                        },
                                        {'content_code_hint': 'capacity'},
                                        {
                                            'text': 'Localized subtitle',
                                            'title': 'Localized title',
                                            'content_code_hint': 'default',
                                            'value': '42',
                                        },
                                        {
                                            'title': 'Free time limit',
                                            'text': 'for toilet and rest',
                                            'content_code_hint': 'default',
                                            'value': '60:00',
                                        },
                                    ],
                                },
                                'requirements': [
                                    {
                                        'is_satisfied': True,
                                        'items': [
                                            {
                                                'captions': {
                                                    'title': 'Lorem ipsum',
                                                    'subtitle': (
                                                        'Dolor sit\namet'
                                                    ),
                                                },
                                                'icon': 'check_failed',
                                                'is_satisfied': False,
                                            },
                                            {
                                                'captions': {
                                                    'title': 'Consectetur',
                                                    'subtitle': '',
                                                },
                                                'icon': 'check_ok',
                                                'is_satisfied': True,
                                            },
                                        ],
                                    },
                                ],
                                'time_range': {
                                    'begin': '2033-04-06T09:00:00+00:00',
                                    'end': '2033-04-06T21:00:00+00:00',
                                },
                                'quota_id': (
                                    'af31c824-066d-46df-0001-100000000001'
                                ),
                                'visibility_info': {},
                            },
                        ],
                        'pin_point': {'lat': 63.0, 'lon': 53.0},
                        'polygon': {
                            'coordinates': [
                                [
                                    {'lat': 62.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 54.0},
                                    {'lat': 64.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 52.0},
                                    {'lat': 62.0, 'lon': 54.0},
                                ],
                            ],
                        },
                        'title': 'The Second Geoarea',
                    },
                ],
            },
        ),
    ],
)
async def test_offer_list_by_geoareas(
        taxi_logistic_supply_conductor,
        pgsql,
        mockserver,
        init_sql,
        add_new_slot,
        viewport,
        driver_id,
        exams,
        exams_times_called,
        expected_response,
):
    if add_new_slot:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(
            """
        INSERT INTO logistic_supply_conductor.workshift_slots
            (workshift_slot_id, workshift_rule_version_id, stored_geoarea_id,
            siblings_group_id, week_day, time_start, time_stop, quota_ref_id)
        VALUES
        (
            '76a3176e-f759-44bc-8fc7-43ea091bd68c',
            3,
            1,
            1,
            'wednesday',
            '2033-04-06T09:00:00Z',
            '2033-04-06T21:00:00Z',
            1
        )
        """,
        )
        cursor.execute(
            """
        INSERT INTO
            logistic_supply_conductor.workshift_slots_migration_statuses
                    (slot_id, migration_state, created_at)
        VALUES
        (
            6,
            'cancelled',
            '2033-04-06T21:00:00Z'
        )
        """,
        )

    for query in init_sql:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(query)

    await taxi_logistic_supply_conductor.invalidate_caches()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/exams/retrieve-by-profiles',
    )
    def unique_driver_exams(request):
        return exams

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/offer/list-by-geoareas',
        json={
            'time_range': {
                'begin': '2033-04-06T00:00:00+03:00',
                'end': '2033-04-07T00:00:00+03:00',
            },
            'viewport_region': viewport,
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': driver_id,
            },
            'offers_filter': {'allowed_transport_types': []},
        },
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    assert unique_driver_exams.times_called == exams_times_called
