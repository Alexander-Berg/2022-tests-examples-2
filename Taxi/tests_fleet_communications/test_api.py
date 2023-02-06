import dateutil
import pytest

AUTH_HEADERS = {
    'X-Yandex-UID': str(998),
    'X-Ya-User-Ticket': 'TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Park-Id': 'PARK-01',
    'X-Idempotency-Token': 'TOKEN-01',
}

AUTH_HEADERS_400 = {
    'X-Yandex-UID': str(998),
    'X-Ya-User-Ticket': 'TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Park-Id': 'PARK-400',
    'X-Idempotency-Token': 'TOKEN-01',
}

AUTH_HEADERS_YATEAM = {
    'X-Yandex-UID': str(998),
    'X-Ya-User-Ticket': 'TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Park-Id': 'PARK-01',
    'X-Idempotency-Token': 'TOKEN-01',
}


def make_config(
        max_message_length=1000,
        max_title_length=120,
        is_enabled_messages=True,
        max_persons=None,
        hour=None,
        delete_time=None,
):
    config = {
        'parks': [],
        'subscriptions': [],
        'default': {
            'restrictions': {
                'is_enabled_messages': is_enabled_messages,
                'limits': {
                    'max_message_length': max_message_length,
                    'max_title_length': max_title_length,
                },
            },
        },
    }
    if max_persons:
        config['default']['restrictions']['limits'][
            'max_persons'
        ] = max_persons
    if hour:
        config['default']['restrictions']['limits']['time_limits'] = {}
        config['default']['restrictions']['limits']['time_limits'][
            'hour'
        ] = hour
    if delete_time:
        config['default']['restrictions']['limits']['delete_limits'] = {}
        config['default']['restrictions']['limits']['delete_limits'][
            'seconds'
        ] = delete_time
    return config


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post(
        mock_api, pg_dump, taxi_fleet_communications, stq,
):
    pg_initial = pg_dump()
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'MESSAGE',
            'title': 'TITLE',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 1
    stq_call = stq.fleet_communications_mailings.next_call()['kwargs']
    stq_call.pop('log_extra')
    assert stq_call == {
        'mailing_id': '612c236a-4082-5af5-a48e-974a504d37c9',
        'park_id': 'PARK-01',
    }
    assert response.status_code == 204, response.text
    assert pg_dump() == {
        **pg_initial,
        'mailings': {
            **pg_initial['mailings'],
            '612c236a-4082-5af5-a48e-974a504d37c9': (
                'PARK-01',
                '612c236a-4082-5af5-a48e-974a504d37c9',
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
                '998',
                None,
                None,
                False,
                None,
                None,
                'CREATED',
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
            ),
        },
        'mailing_templates': {
            **pg_initial['mailing_templates'],
            '612c236a-4082-5af5-a48e-974a504d37c9': (
                'PARK-01',
                ['WORK_RULE'],
                '{busy}',
                ['CATEGORY'],
                ['AMENITY'],
                '{none}',
                ['permanent'],
                ['CONTRACTOR-10'],
                ['CONTRACTOR-20'],
                'TITLE',
                'MESSAGE',
                dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
                '998',
            ),
        },
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_400(
        mock_api, pg_dump, taxi_fleet_communications, stq,
):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS_400,
        json={'message': 'MESSAGE'},
    )
    assert stq.fleet_communications_mailings.times_called == 0
    assert response.status_code == 400, response.text
    assert response.json() == {'code': 'bad_request', 'message': ''}


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_not_allowed(
        mock_api, pg_dump, taxi_fleet_communications, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                is_enabled_messages=False,
            ),
        },
    )
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'MESSAGE',
            'title': 'TITLE',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': 'mailing_not_allowed',
        'message': 'mailing not allowed',
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_limit_exceed(
        mock_api, pg_dump, taxi_fleet_communications, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                max_persons=1,
            ),
        },
    )
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'MESSAGE',
            'title': 'TITLE',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': 'limit_drivers',
        'message': 'Max person amount in mailing 1, but it\'s 3 now',
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_msg_limit_exceed(
        mock_api, pg_dump, taxi_fleet_communications, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                max_message_length=3,
            ),
        },
    )
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'Сообщение',
            'title': 'TITLE',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': 'message_too_long',
        'message': 'message is too long (9 > 3)',
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_title_limit_exceed(
        mock_api, pg_dump, taxi_fleet_communications, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                max_title_length=3,
            ),
        },
    )
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'MESSAGE',
            'title': 'Заголовок',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': 'title_too_long',
        'message': 'title is too long (9 > 3)',
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_limit_utf8(
        mock_api, pg_dump, taxi_fleet_communications, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                max_title_length=9, max_message_length=10,
            ),
        },
    )
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'Сообщение',
            'title': 'Заголовок',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 1
    assert response.status_code == 204


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_post_limit_time_exceed(
        mock_api, pg_dump, taxi_fleet_communications, stq, taxi_config,
):
    taxi_config.set_values(
        {'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(hour=1)},
    )
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        json={
            'message': 'MESSAGE',
            'title': 'TITLE',
            'included_contractor_ids': ['CONTRACTOR-10'],
            'excluded_contractor_ids': ['CONTRACTOR-20'],
            'filters': {
                'work_rule_ids': ['WORK_RULE'],
                'car_categories': ['CATEGORY'],
                'car_amenities': ['AMENITY'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'affiliation_partner_sources': ['none'],
            },
        },
    )
    assert stq.fleet_communications_mailings.times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': 'limit_time',
        'message': 'time restriction',
        'available_at': '2022-01-02T13:01:00+00:00',
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_get(mock_api, pg_dump, taxi_fleet_communications):
    response = await taxi_fleet_communications.get(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-01'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'mailing_template': {
            'excluded_contractor_ids': ['CONTRACTOR-04'],
            'filters': {
                'affiliation_partner_sources': ['none'],
                'car_amenities': ['wifi'],
                'car_categories': ['econom'],
                'deptrans_statuses': ['permanent'],
                'driver_statuses': ['busy'],
                'work_rule_ids': ['WORK_RULE-01'],
            },
            'included_contractor_ids': ['CONTRACTOR-03', 'CONTRACTOR-04'],
            'message': 'MESSAGE{}',
            'title': 'TITLE{}',
        },
        'mailing_summary': {
            'author': '999_NAME',
            'id': 'MAILING-01',
            'preview': 'TITLE{}',
            'is_legacy': False,
        },
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_get_404(mock_api, pg_dump, taxi_fleet_communications):
    response = await taxi_fleet_communications.get(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-404'},
    )
    assert response.status_code == 404, response.text


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailing_delete_by_admin(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.delete(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS_YATEAM,
        params={'id': 'MAILING-02'},
    )
    assert response.status_code == 204


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailing_delete_by_user(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.delete(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-02'},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'delete_unavailible',
        'message': 'Mailing removing is unavailible',
    }


@pytest.mark.now('2022-01-01T12:00:05+00:00')
async def test_mailing_delete_by_user_ok(
        mock_api, pg_dump, taxi_fleet_communications, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                delete_time=10,
            ),
        },
    )
    response = await taxi_fleet_communications.delete(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-02'},
    )
    assert response.status_code == 204, response.text


@pytest.mark.now('2022-01-01T12:00:11+00:00')
async def test_mailing_delete_by_user_time_limit(
        mock_api, pg_dump, taxi_fleet_communications, taxi_config,
):
    taxi_config.set_values(
        {
            'FLEET_COMMUNICATIONS_MAILINGS_RESTRICTIONS': make_config(
                delete_time=10,
            ),
        },
    )
    response = await taxi_fleet_communications.delete(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-02'},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'time_limit',
        'message': 'Mailing removing is availible just for 10 seconds',
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailing_delete_404(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.delete(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-404'},
    )
    assert response.status_code == 404, response.text


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailing_delete_deleted(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.delete(
        '/fleet/communications/v1/mailings',
        headers=AUTH_HEADERS,
        params={'id': 'MAILING-03'},
    )
    assert response.status_code == 204, response.text


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_list(mock_api, pg_dump, taxi_fleet_communications):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings/list',
        headers=AUTH_HEADERS,
        json={},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'mailings': [
            {
                'author': '999_NAME',
                'id': 'MAILING-04',
                'preview': 'TITLE{}',
                'is_legacy': False,
                'status': 'created',
            },
            {
                'author': '999_NAME',
                'id': 'MAILING-01',
                'preview': 'TITLE{}',
                'is_legacy': False,
                'status': 'created',
            },
            {
                'author': '999_NAME',
                'id': 'MAILING-05',
                'preview': 'TITLE{}',
                'sent_at': '2022-03-01T12:00:01+00:00',
                'sent_to_number': 555,
                'is_legacy': False,
                'status': 'deleted_by_dispatcher',
                'deleted_at': '2022-03-01T12:01:00+00:00',
                'deleted_by': 'dispather_NAME',
            },
            {
                'author': '999_NAME',
                'deleted_at': '2022-01-02T12:00:00+00:00',
                'id': 'MAILING-03',
                'is_legacy': False,
                'preview': 'TITLE{}',
                'sent_at': '2022-01-01T12:00:00+00:00',
                'sent_to_number': 555,
                'status': 'deleted_by_admin',
            },
            {
                'author': '999_NAME',
                'id': 'MAILING-02',
                'preview': 'TITLE{}',
                'sent_at': '2022-01-01T12:00:00+00:00',
                'sent_to_number': 555,
                'is_legacy': False,
                'status': 'sent',
            },
        ],
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_list_cursor(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings/list',
        headers=AUTH_HEADERS,
        json={'limit': 2},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'mailings': [
            {
                'author': '999_NAME',
                'id': 'MAILING-04',
                'preview': 'TITLE{}',
                'is_legacy': False,
                'status': 'created',
            },
            {
                'author': '999_NAME',
                'id': 'MAILING-01',
                'preview': 'TITLE{}',
                'is_legacy': False,
                'status': 'created',
            },
        ],
        'cursor': 'eyJzZW50X2F0IjoiMjAyMi0wMS0wMlQxMjowMDowMCswMDowMCIsImlkIjoiTUFJTElORy0wMSJ9',  # noqa E501
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_list_cursor_in_query(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings/list',
        headers=AUTH_HEADERS,
        json={
            'cursor': 'eyJzZW50X2F0IjoiMjAyMi0wMS0wMVQxMjowMDowMCswMDowMCIsImlkIjoiTUFJTElORy0wMyJ9',  # noqa E501
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'mailings': [
            {
                'author': '999_NAME',
                'id': 'MAILING-02',
                'preview': 'TITLE{}',
                'sent_at': '2022-01-01T12:00:00+00:00',
                'sent_to_number': 555,
                'is_legacy': False,
                'status': 'sent',
            },
        ],
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_list_cursor_in_query_same_time(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings/list',
        headers=AUTH_HEADERS,
        json={
            'cursor': 'eyJzZW50X2F0IjoiMjAyMi0wMS0wMlQxMjowMDowMCswMDowMCIsImlkIjoiTUFJTElORy0wMSJ9',  # noqa E501
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'mailings': [
            {
                'author': '999_NAME',
                'deleted_at': '2022-01-02T12:00:00+00:00',
                'id': 'MAILING-03',
                'is_legacy': False,
                'preview': 'TITLE{}',
                'sent_at': '2022-01-01T12:00:00+00:00',
                'sent_to_number': 555,
                'status': 'deleted_by_admin',
            },
            {
                'author': '999_NAME',
                'id': 'MAILING-02',
                'preview': 'TITLE{}',
                'sent_at': '2022-01-01T12:00:00+00:00',
                'sent_to_number': 555,
                'is_legacy': False,
                'status': 'sent',
            },
        ],
    }


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_list_empty(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings/list',
        headers=AUTH_HEADERS_400,
        json={},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'mailings': []}


@pytest.mark.now('2022-01-02T12:00:00+00:00')
async def test_mailings_list_cursor_incorrect(
        mock_api, pg_dump, taxi_fleet_communications,
):
    response = await taxi_fleet_communications.post(
        '/fleet/communications/v1/mailings/list',
        headers=AUTH_HEADERS,
        json={'cursor': 'LALALA'},
    )
    assert response.status_code == 400, response.text
