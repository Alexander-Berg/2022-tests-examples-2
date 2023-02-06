import pytest

PARK_ID = '458f82d8dbf24ecd81d1de2c7826d1b5'
DRIVER_ID = 'e2b66c10ece54751a8db96b3a2039b0f'


EXPECTED_TAG = (
    'on_logistic_workshift_af31c824-066d-46df-0001-000000000002'
    '_at_logistic_supply_second'
)


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'Timezone': 'Europe/Moscow',
    'X-Remote-IP': '12.34.56.78',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


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
        'pg_descriptive_items_for_offers.sql',
    ],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_CANCELLATION_SETTINGS_BY_COUNTRY={
        'ru': {
            'cancelation_offer_ttl': 300,
            'penalties': [
                {
                    'time_left_until_workshift_start': 1000000000,
                    'fine_value': '1000',
                },
                {
                    'time_left_until_workshift_start': 1000,
                    'fine_value': '2000',
                },
            ],
            'currency_code': 'RUB',
        },
    },
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
    'init_sql, request_json, response_code, expected_response',
    [
        (
            [
                f"""
            INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
            (contractor_id, slot_id, subscribed_at,
            idempotency, free_time_left)
            VALUES
            (
                '({PARK_ID},{DRIVER_ID})',
                1,
                CURRENT_TIMESTAMP - '1 hour'::interval,
                'some',
                '00:12:34'
            );
            """,
            ],
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'slots': [
                    {
                        'actual_offer': {
                            'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                            'rule_version': 2,
                        },
                    },
                    {
                        'actual_offer': {
                            'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                            'rule_version': 2,
                        },
                        'previous_offer': {
                            'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                            'rule_version': 1,
                        },
                    },
                ],
            },
            200,
            {
                'slots': [
                    {
                        'info': {
                            'identity': {
                                'slot_id': (
                                    '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                ),
                                'rule_version': 2,
                            },
                            'item_view': {
                                'captions': {
                                    'title': '11:00—23:00',
                                    'subtitle': 'The Second Geoarea',
                                },
                                'icon': 'in_progress',
                            },
                            'activation_state': 'started',
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                            'description': {
                                'captions': {
                                    'title': 'The Second Geoarea',
                                    'subtitle': 'Slot is active',
                                },
                                'icon': 'in_progress',
                                'items': [
                                    {
                                        'title': 'Schedule',
                                        'content_code_hint': 'default',
                                        'value': '11:00—23:00',
                                    },
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
                                        'value': '12:34',
                                    },
                                ],
                            },
                            'quota_id': 'af31c824-066d-46df-0001-100000000001',
                            'requirements': [
                                {
                                    'dissatisfied_audit_reasons': [
                                        'foo',
                                        'bar',
                                    ],
                                    'is_satisfied': False,
                                    'items': [
                                        {
                                            'captions': {
                                                'subtitle': (
                                                    'Dolor ' 'sit\n' 'amet'
                                                ),
                                                'title': 'Lorem ' 'ipsum',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                        {
                                            'captions': {
                                                'subtitle': '',
                                                'title': 'Consectetur',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                    ],
                                },
                            ],
                            'time_range': {
                                'begin': '2033-04-06T08:00:00+00:00',
                                'end': '2033-04-06T20:00:00+00:00',
                            },
                            'cancellation_opportunity': {
                                'offer': {
                                    'fine_value': {
                                        'currency_code': 'RUB',
                                        'value': '1000',
                                    },
                                },
                            },
                            'actions': [
                                {
                                    'action_type': 'pause',
                                    'icon': 'pause',
                                    'label': 'Take a break',
                                    'dialog_title': 'Go to pause?',
                                    'dialog_message': 'Are you sure?',
                                    'dialog_close_button': 'Yup!',
                                },
                                {
                                    'action_type': 'stop',
                                    'icon': 'stop',
                                    'is_active': True,
                                    'is_in_progress': False,
                                    'label': 'Leave slot\n-1000 ₽',
                                },
                            ],
                        },
                    },
                    {
                        'info': {
                            'identity': {
                                'slot_id': (
                                    '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3'
                                ),
                                'rule_version': 2,
                            },
                            'item_view': {
                                'captions': {
                                    'title': '11:00—23:00',
                                    'subtitle': 'The Second Geoarea',
                                },
                                'icon': 'forbidden',
                            },
                            'activation_state': 'waiting',
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                            'description': {
                                'captions': {
                                    'title': 'The Second Geoarea',
                                    'subtitle': 'Requirements not satisfied',
                                },
                                'subtitle_highlight': 'danger',
                                'icon': 'forbidden',
                                'items': [
                                    {
                                        'title': 'Schedule',
                                        'content_code_hint': 'default',
                                        'value': '11:00—23:00',
                                    },
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
                            'quota_id': 'af31c824-066d-46df-0001-100000000003',
                            'requirements': [
                                {
                                    'dissatisfied_audit_reasons': [
                                        'foo',
                                        'bar',
                                    ],
                                    'is_satisfied': False,
                                    'items': [
                                        {
                                            'captions': {
                                                'subtitle': (
                                                    'Dolor ' 'sit\n' 'amet'
                                                ),
                                                'title': 'Lorem ' 'ipsum',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                        {
                                            'captions': {
                                                'subtitle': '',
                                                'title': 'Consectetur',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                    ],
                                },
                            ],
                            'time_range': {
                                'begin': '2033-04-10T08:00:00+00:00',
                                'end': '2033-04-10T20:00:00+00:00',
                            },
                            'cancellation_opportunity': {
                                'offer': {
                                    'fine_value': {
                                        'currency_code': 'RUB',
                                        'value': '1000',
                                    },
                                },
                            },
                            'actions': [
                                {
                                    'action_type': 'cancel',
                                    'icon': 'stop',
                                    'is_active': True,
                                    'is_in_progress': False,
                                    'label': 'Cancel slot\n-1000 ₽',
                                },
                            ],
                        },
                        'changes': {
                            'after': [
                                {
                                    'title': 'Schedule',
                                    'content_code_hint': 'default',
                                    'value': '11:00—23:00',
                                },
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
                            'before': [
                                {
                                    'title': 'Schedule',
                                    'content_code_hint': 'default',
                                    'value': '11:00—23:00',
                                },
                                {
                                    'title': 'Free time limit',
                                    'text': 'for toilet and rest',
                                    'content_code_hint': 'default',
                                    'value': '1:00',
                                },
                            ],
                            'item_view_subtitle': 'Offer changed',
                            'title': 'Offer have been changed',
                            'title_after': 'After',
                            'title_before': 'Before',
                        },
                    },
                ],
            },
        ),
        (
            [
                f"""
            INSERT INTO logistic_supply_conductor.workshift_slot_subscribers
            (contractor_id, slot_id, subscribed_at,
            idempotency, free_time_end)
            VALUES
            ('({PARK_ID},{DRIVER_ID})', 1, CURRENT_TIMESTAMP,
            'some', '2033-12-31T12:34Z');
            """,
                """
            UPDATE logistic_supply_conductor.workshift_slots
            SET time_start = '2000-01-01T00:00:00Z',
                time_stop = '2000-01-01T00:00:01Z'
            WHERE workshift_slot_id = '76a3176e-f759-44bc-8fc7-43ea091bd68b'
            """,
            ],
            {
                'contractor_id': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_ID,
                },
                'slots': [
                    {
                        'actual_offer': {
                            'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                            'rule_version': 2,
                        },
                    },
                    {
                        'actual_offer': {
                            'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                            'rule_version': 2,
                        },
                        'previous_offer': {
                            'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                            'rule_version': 1,
                        },
                    },
                ],
            },
            200,
            {
                'slots': [
                    {
                        'info': {
                            'identity': {
                                'slot_id': (
                                    '76a3176e-f759-44bc-8fc7-43ea091bd68b'
                                ),
                                'rule_version': 2,
                            },
                            'item_view': {
                                'captions': {
                                    'title': '03:00—03:00',
                                    'subtitle': 'The Second Geoarea',
                                },
                                'icon': 'completed',
                            },
                            'activation_state': 'starting',
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                            'description': {
                                'captions': {
                                    'title': 'The Second Geoarea',
                                    'subtitle': 'Slot is finished',
                                },
                                'icon': 'completed',
                                'items': [
                                    {
                                        'title': 'Schedule',
                                        'content_code_hint': 'default',
                                        'value': '03:00—03:00',
                                    },
                                    {
                                        'text': 'Localized subtitle',
                                        'title': 'Localized title',
                                        'content_code_hint': 'default',
                                        'value': '42',
                                    },
                                    {
                                        'title': 'Free time limit',
                                        'text': 'for toilet and rest',
                                        'free_time_end': (
                                            '2033-12-31T12:34:00+00:00'
                                        ),
                                        'extra_time_end': (
                                            '2033-12-31T12:34:00+00:00'
                                        ),
                                        'value': '2033-12-31T12:34:00+00:00',
                                        'content_code_hint': (
                                            'expiration_timestamp'
                                        ),
                                    },
                                ],
                            },
                            'quota_id': 'af31c824-066d-46df-0001-100000000001',
                            'requirements': [
                                {
                                    'dissatisfied_audit_reasons': [
                                        'foo',
                                        'bar',
                                    ],
                                    'is_satisfied': False,
                                    'items': [
                                        {
                                            'captions': {
                                                'subtitle': (
                                                    'Dolor ' 'sit\n' 'amet'
                                                ),
                                                'title': 'Lorem ' 'ipsum',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                        {
                                            'captions': {
                                                'subtitle': '',
                                                'title': 'Consectetur',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                    ],
                                },
                            ],
                            'time_range': {
                                'begin': '2000-01-01T00:00:00+00:00',
                                'end': '2000-01-01T00:00:01+00:00',
                            },
                            'cancellation_opportunity': {
                                'offer': {
                                    'fine_value': {
                                        'currency_code': 'RUB',
                                        'value': '2000',
                                    },
                                },
                            },
                            'actions': [],
                        },
                    },
                    {
                        'info': {
                            'identity': {
                                'slot_id': (
                                    '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3'
                                ),
                                'rule_version': 2,
                            },
                            'item_view': {
                                'captions': {
                                    'title': '11:00—23:00',
                                    'subtitle': 'The Second Geoarea',
                                },
                                'icon': 'forbidden',
                            },
                            'activation_state': 'waiting',
                            'allowed_transport_types': [
                                'pedestrian',
                                'auto',
                                'bicycle',
                            ],
                            'description': {
                                'captions': {
                                    'title': 'The Second Geoarea',
                                    'subtitle': 'Requirements not satisfied',
                                },
                                'subtitle_highlight': 'danger',
                                'icon': 'forbidden',
                                'items': [
                                    {
                                        'title': 'Schedule',
                                        'content_code_hint': 'default',
                                        'value': '11:00—23:00',
                                    },
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
                            'quota_id': 'af31c824-066d-46df-0001-100000000003',
                            'requirements': [
                                {
                                    'dissatisfied_audit_reasons': [
                                        'foo',
                                        'bar',
                                    ],
                                    'is_satisfied': False,
                                    'items': [
                                        {
                                            'captions': {
                                                'subtitle': (
                                                    'Dolor ' 'sit\n' 'amet'
                                                ),
                                                'title': 'Lorem ' 'ipsum',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                        {
                                            'captions': {
                                                'subtitle': '',
                                                'title': 'Consectetur',
                                            },
                                            'icon': 'check_failed',
                                            'is_satisfied': False,
                                        },
                                    ],
                                },
                            ],
                            'time_range': {
                                'begin': '2033-04-10T08:00:00+00:00',
                                'end': '2033-04-10T20:00:00+00:00',
                            },
                            'cancellation_opportunity': {
                                'offer': {
                                    'fine_value': {
                                        'currency_code': 'RUB',
                                        'value': '1000',
                                    },
                                },
                            },
                            'actions': [
                                {
                                    'action_type': 'cancel',
                                    'icon': 'stop',
                                    'is_active': True,
                                    'is_in_progress': False,
                                    'label': 'Cancel slot\n-1000 ₽',
                                },
                            ],
                        },
                        'changes': {
                            'after': [
                                {
                                    'title': 'Schedule',
                                    'content_code_hint': 'default',
                                    'value': '11:00—23:00',
                                },
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
                            'before': [
                                {
                                    'title': 'Schedule',
                                    'content_code_hint': 'default',
                                    'value': '11:00—23:00',
                                },
                                {
                                    'title': 'Free time limit',
                                    'text': 'for toilet and rest',
                                    'content_code_hint': 'default',
                                    'value': '1:00',
                                },
                            ],
                            'item_view_subtitle': 'Offer changed',
                            'title': 'Offer have been changed',
                            'title_after': 'After',
                            'title_before': 'Before',
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_offer_info_list(
        taxi_logistic_supply_conductor,
        pgsql,
        init_sql,
        request_json,
        response_code,
        expected_response,
):
    for query in init_sql:
        cursor = pgsql['logistic_supply_conductor'].cursor()
        cursor.execute(query)

    await taxi_logistic_supply_conductor.invalidate_caches()

    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/offer/info/list',
        json=request_json,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == response_code
    assert response.json() == expected_response
