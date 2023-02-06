import pytest

PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID = 'e2b66c10ece54751a8db96b3a2039b0f'


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Timezone': 'Europe/Moscow',
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


SHIFTED_VEWPORT = {
    'top_left': {'lat': 73.5, 'lon': 52.5},
    'bottom_right': {'lat': 72.5, 'lon': 53.5},
}


PARTIALLY_COVERING_VEWPORT = {
    'top_left': {'lat': 64.5, 'lon': 51.5},
    'bottom_right': {'lat': 63.5, 'lon': 52.5},
}


@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID}', 'foo1'),
        ('dbid_uuid', f'{PARK_ID}_{DRIVER_ID}', 'bar2'),
    ],
)
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='logistic_supply_conductor_contractor_professions',
    consumers=['logistic-supply-conductor/contractor-profession'],
    clauses=[],
    default_value={
        'enabled': False,
        'mappings': [{'profession': 'fisher', 'tag': 'bar2'}],
    },
    is_config=True,
)
@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_courier_requirements.sql',
    ],
)
@pytest.mark.parametrize(
    'init_sql, viewport, expected_response',
    [
        (None, DEFAULT_VEWPORT, {'days': []}),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            DEFAULT_VEWPORT,
            {
                'days': [
                    {
                        'date_description': {
                            'date': '2033-04-06',
                            'time_range': {
                                'begin': '2033-04-05T21:00:00+00:00',
                                'end': '2033-04-06T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 64, 'lon': 52},
                            'bottom_right': {'lat': 62, 'lon': 54},
                        },
                    },
                    {
                        'date_description': {
                            'date': '2033-04-08',
                            'time_range': {
                                'begin': '2033-04-07T21:00:00+00:00',
                                'end': '2033-04-08T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 64, 'lon': 52},
                            'bottom_right': {'lat': 62, 'lon': 54},
                        },
                    },
                ],
            },
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            PARTIALLY_COVERING_VEWPORT,
            {
                'days': [
                    {
                        'date_description': {
                            'date': '2033-04-06',
                            'time_range': {
                                'begin': '2033-04-05T21:00:00+00:00',
                                'end': '2033-04-06T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 64, 'lon': 52},
                            'bottom_right': {'lat': 62, 'lon': 54},
                        },
                    },
                    {
                        'date_description': {
                            'date': '2033-04-08',
                            'time_range': {
                                'begin': '2033-04-07T21:00:00+00:00',
                                'end': '2033-04-08T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 64, 'lon': 52},
                            'bottom_right': {'lat': 62, 'lon': 54},
                        },
                    },
                ],
            },
        ),
        (
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2
            """,
            SHIFTED_VEWPORT,
            {'days': []},
        ),
        pytest.param(
            """
            UPDATE logistic_supply_conductor.workshift_metadata
            SET
                is_visible = true,
                visibility_duration = '90 years'::interval,
                visibility_end_date = '2033-04-11T00:00:00Z'
            WHERE rule_id = 2
            """,
            SHIFTED_VEWPORT,
            {
                'days': [
                    {
                        'date_description': {
                            'date': '2033-04-06',
                            'time_range': {
                                'begin': '2033-04-05T21:00:00+00:00',
                                'end': '2033-04-06T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 65, 'lon': 51},
                            'bottom_right': {'lat': 61, 'lon': 55},
                        },
                    },
                    {
                        'date_description': {
                            'date': '2033-04-08',
                            'time_range': {
                                'begin': '2033-04-07T21:00:00+00:00',
                                'end': '2033-04-08T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 65, 'lon': 51},
                            'bottom_right': {'lat': 61, 'lon': 55},
                        },
                    },
                    {
                        'date_description': {
                            'date': '2033-04-10',
                            'time_range': {
                                'begin': '2033-04-09T21:00:00+00:00',
                                'end': '2033-04-10T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 65, 'lon': 51},
                            'bottom_right': {'lat': 61, 'lon': 55},
                        },
                    },
                ],
            },
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_OFFER_DISPLAY_SETTINGS={
                    'viewport_minimal_lat_height': 40,
                    'viewport_minimal_lon_width': 6,
                    'viewport_demagnification_ratio': 2,
                },
            ),
        ),
        (
            """
            UPDATE logistic_supply_conductor.courier_requirements
            SET
                expression = '{"operator":"nor","tags":["bar1","bar2"]}',
                passthrough_revision=
                    NEXTVAL('courier_requirements_passthrough_revision_seq');
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2;
            """,
            DEFAULT_VEWPORT,
            {'days': []},
        ),
        (
            """
            UPDATE logistic_supply_conductor.courier_requirements
            SET
                expression = '{"operator":"and","tags":["bar1","bar2"]}',
                passthrough_revision=
                    NEXTVAL('courier_requirements_passthrough_revision_seq');
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2;
            """,
            DEFAULT_VEWPORT,
            {'days': []},
        ),
        (
            """
            UPDATE logistic_supply_conductor.courier_requirements
            SET
                expression = '{"operator":"or","tags":["bar1","bar2"]}',
                passthrough_revision=
                    NEXTVAL('courier_requirements_passthrough_revision_seq');
            UPDATE logistic_supply_conductor.workshift_metadata
            SET is_visible = true, visibility_duration = '90 years'::interval
            WHERE rule_id = 2;
            """,
            DEFAULT_VEWPORT,
            {
                'days': [
                    {
                        'date_description': {
                            'date': '2033-04-06',
                            'time_range': {
                                'begin': '2033-04-05T21:00:00+00:00',
                                'end': '2033-04-06T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 64, 'lon': 52},
                            'bottom_right': {'lat': 62, 'lon': 54},
                        },
                    },
                    {
                        'date_description': {
                            'date': '2033-04-08',
                            'time_range': {
                                'begin': '2033-04-07T21:00:00+00:00',
                                'end': '2033-04-08T21:00:00+00:00',
                            },
                        },
                        'viewport_suggest': {
                            'top_left': {'lat': 64, 'lon': 52},
                            'bottom_right': {'lat': 62, 'lon': 54},
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_offer_calendar(
        taxi_logistic_supply_conductor,
        pgsql,
        init_sql,
        viewport,
        expected_response,
):
    if init_sql is not None:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(init_sql)

    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/offer/calendar',
        json={
            'contractor_position': {'lat': 63, 'lon': 53},
            'viewport_region': viewport,
            'contractor_id': {
                'park_id': PARK_ID,
                'driver_profile_id': DRIVER_ID,
            },
            'offers_filter': {'allowed_transport_types': []},
        },
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == expected_response
