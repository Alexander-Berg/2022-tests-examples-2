# pylint: disable=too-many-lines
import datetime

import pytest

from support_info.api import tags

NOW = datetime.datetime(2019, 4, 9, 12, 35, 55, tzinfo=datetime.timezone.utc)
ONE_DAY_AGO = NOW - datetime.timedelta(days=1)
ONE_YEAR_AGO = NOW - datetime.timedelta(days=365)

TRANSLATIONS = {
    'tags.driver_rudeness': {
        'ru': 'грубость водителя',
        'en': 'driver rudeness',
    },
    'tags.driver_cancels_orders': {
        'ru': 'водитель отменяет заказ',
        'en': 'driver cancels order',
    },
    'tags.driver_wants_promo': {
        'ru': 'выпрашивает промокоды',
        'en': 'driver wants promo',
    },
    'tags.passenger_cancels_orders': {
        'ru': 'отменяет заказы',
        'en': 'passenger cancels orders',
    },
    'tags.passenger_run_away_without_payment': {
        'ru': 'сбегает не оплатив',
        'en': 'passenger runs away without payment for order',
    },
    'tags.phone_tag': {'ru': 'some_phone_tag'},
    'tags.phone_pd_id_tag': {'ru': 'some_phone_pd_id_tag'},
    'tags.support_tag': {'ru': 'some_support_tag'},
}


# pylint: disable=too-many-arguments
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(support_info=TRANSLATIONS)
@pytest.mark.parametrize(['version'], [('v1',), ('v2',)])
@pytest.mark.parametrize(
    [
        'query',
        'chatterbox_tickets',
        'zendesk_tickets',
        'expected_result',
        'zendesk_called',
        'chatterbox_called_params',
        'modify_config',
    ],
    [
        (
            {'user': 'client', 'identification': '+790001233322'},
            [
                {
                    'id': '1',
                    'created': ONE_DAY_AGO.isoformat(),
                    'tags': [
                        'dr_info_feedback_about_rider_excessive_',
                        'rd_fare_cancel_driver_canceled',  # driver tag
                    ],
                },
            ],
            [
                {
                    'tags': [
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        'dr_info_feedback_about_rider_excessive_'
                        'cancellations',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        'dr_info_feedback_about_rider_excessive_'
                        'cancellations',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        'dr_info_feedback_about_rider_excessive_'
                        'cancellations',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        'dr_info_feedback_about_rider_excessive_'
                        'cancellations',
                    ],
                    'created': ONE_YEAR_AGO.isoformat(),
                },
                {
                    'tags': [
                        'dr_info_feedback_about_rider_excessive_'
                        'cancellations',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            {
                'items': [{'number': 4, 'tag': 'отменяет заказы'}],
                'status': 'ok',
                'threshold': 3,
                'number_days': 60,
            },
            [
                {
                    'args': (),
                    'kwargs': {
                        'query_args': ['created<2019-02-08'],
                        'query_kwargs': {
                            'requester': '790001233322@taxi.yandex.ru',
                            'type': 'ticket',
                        },
                    },
                },
            ],
            {'created_from': '2019-02-08', 'user_phone': '+790001233322'},
            False,
        ),
        (
            {'user': 'driver', 'identification': 'itsdriverlicence'},
            [
                {
                    'id': '1',
                    'tags': ['макрос_почему_не_дали_промик'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': '2',
                    'tags': ['макрос_почему_не_дали_промик'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                # passenger tag
                {
                    'id': '3',
                    'tags': ['rd_fare_ufp_correct'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            [
                {
                    'tags': ['rd_fare_cancel_driver_canceled'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        # passenger tag
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                        'rd_fare_cancel_driver_canceled',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': ['rd_fare_cancel_driver_canceled'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        # passenger tag
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                        'rd_fare_cancel_driver_canceled',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            {
                'items': [{'number': 4, 'tag': 'водитель отменяет заказ'}],
                'status': 'ok',
                'threshold': 3,
                'number_days': 60,
            },
            [
                {
                    'args': (),
                    'kwargs': {
                        'query_args': ['created<2019-02-08'],
                        'query_kwargs': {
                            'requester': 'itsdriverlicence@taximeter.ru',
                            'type': 'ticket',
                        },
                    },
                },
            ],
            {
                'created_from': '2019-02-08',
                'driver_license': 'itsdriverlicence',
            },
            False,
        ),
        (
            {'user': 'driver', 'identification': 'itsdriverlicence'},
            [
                {
                    'id': '1',
                    'tags': ['макрос_почему_не_дали_промик'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': '2',
                    'tags': ['макрос_почему_не_дали_промик'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                # passenger tag
                {
                    'id': '3',
                    'tags': ['rd_fare_ufp_correct'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            [
                {
                    'tags': ['rd_fare_cancel_driver_canceled'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        # passenger tag
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                        'rd_fare_cancel_driver_canceled',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': ['rd_fare_cancel_driver_canceled'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        # passenger tag
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                        'rd_fare_cancel_driver_canceled',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            {
                'items': [
                    {'number': 4, 'tag': 'водитель отменяет заказ'},
                    {'number': 2, 'tag': 'выпрашивает промокоды'},
                ],
                'status': 'ok',
                'threshold': 3,
                'number_days': 61,
            },
            [
                {
                    'args': (),
                    'kwargs': {
                        'query_args': ['created<2019-02-07'],
                        'query_kwargs': {
                            'requester': 'itsdriverlicence@taximeter.ru',
                            'type': 'ticket',
                        },
                    },
                },
            ],
            {
                'created_from': '2019-02-07',
                'driver_license': 'itsdriverlicence',
            },
            True,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_tags(
        mock_personal_single_response,
        support_info_app,
        support_info_client,
        version,
        query,
        chatterbox_tickets,
        zendesk_tickets,
        expected_result,
        zendesk_called,
        chatterbox_called_params,
        mock_chatterbox_search,
        mock_zendesk_search,
        mock_tvm_get_service_name,
        modify_config,
):
    if modify_config:
        last_general_tag = (
            support_info_app.config.SUPPORT_INFO_DRIVER_TAG_CONDITIONS[-1]
        )
        last_general_tag['day_limit'] = 61
        last_general_tag['threshold'] = 2

    mock_chatterbox_search.set_response({'tasks': chatterbox_tickets})
    # mock_zendesk_search will be called twice for every zendesk profile
    # yandex and uber
    mock_zendesk_search.set_response({'results': zendesk_tickets})
    mock_personal_single_response(query['identification'])
    response = await support_info_client.get(
        '/{}/tags/{}/{}'.format(
            version, query['user'], query['identification'],
        ),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    assert response.status == 200
    assert await response.json() == expected_result

    assert mock_zendesk_search.calls == zendesk_called
    chat_called = mock_chatterbox_search.call['kwargs']
    assert chat_called['data'] == chatterbox_called_params


@pytest.mark.config(
    SUPPORT_INFO_DRIVER_TAG_CONDITIONS=[
        {
            'tanker_key': 'tags.driver_rudeness',
            'tags': ['rd_feedback_quality_professionalism_rude_driver'],
            'day_limit': 60,
            'threshold': 3,
        },
        {
            'tanker_key': 'tags.driver_cancels_orders',
            'tags': [
                'rd_fare_cancel_driver_canceled',
                'макрос_почему_не_дали_промик',
            ],
            'day_limit': 60,
            'threshold': 3,
        },
        {
            'tanker_key': 'tags.driver_requires_to_pay_more',
            'tags': ['rd_fare_extra_cash_driver_error_asked_more'],
            'day_limit': 60,
            'threshold': 3,
        },
        {
            'tanker_key': 'tags.driver_wants_promo',
            'tags': [
                'макрос_почему_не_дали_промик',
                'макрос_почему_не_дали_промик',
            ],
            'day_limit': 61,
            'threshold': 2,
        },
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(support_info=TRANSLATIONS)
@pytest.mark.parametrize(
    [
        'query',
        'chatterbox_tickets',
        'zendesk_tickets',
        'expected_result',
        'zendesk_called',
        'chatterbox_called_params',
    ],
    [
        (
            {'user': 'driver', 'identification': 'itsdriverlicence'},
            [
                {
                    'id': '1',
                    'tags': ['макрос_почему_не_дали_промик'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': '2',
                    'tags': ['макрос_почему_не_дали_промик'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                # passenger tag
                {
                    'id': '3',
                    'tags': ['rd_fare_ufp_correct'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            [
                {
                    'tags': ['rd_fare_cancel_driver_canceled'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        # passenger tag
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                        'rd_fare_cancel_driver_canceled',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': ['rd_fare_cancel_driver_canceled'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': [
                        # passenger tag
                        'dr_fare_review_cash_trip_rider_error_not_payment',
                        'rd_fare_cancel_driver_canceled',
                    ],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
            {
                'items': [
                    {'number': 6, 'tag': 'водитель отменяет заказ'},
                    {'number': 2, 'tag': 'выпрашивает промокоды'},
                ],
                'status': 'ok',
                'threshold': 3,
                'number_days': 61,
            },
            [
                {
                    'args': (),
                    'kwargs': {
                        'query_args': ['created<2019-02-07'],
                        'query_kwargs': {
                            'requester': 'itsdriverlicence@taximeter.ru',
                            'type': 'ticket',
                        },
                    },
                },
            ],
            {
                'created_from': '2019-02-07',
                'driver_license': 'itsdriverlicence',
            },
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_same_tags_in_several_conditions(
        mock_personal_single_response,
        support_info_client,
        query,
        chatterbox_tickets,
        zendesk_tickets,
        expected_result,
        zendesk_called,
        chatterbox_called_params,
        mock_chatterbox_search,
        mock_zendesk_search,
        mock_tvm_get_service_name,
):

    mock_chatterbox_search.set_response({'tasks': chatterbox_tickets})
    mock_zendesk_search.set_response({'results': zendesk_tickets})
    mock_personal_single_response(query['identification'])
    response = await support_info_client.get(
        '/v2/tags/{}/{}'.format(query['user'], query['identification']),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    assert response.status == 200
    assert await response.json() == expected_result

    assert mock_zendesk_search.calls == zendesk_called
    chat_called = mock_chatterbox_search.call['kwargs']
    assert chat_called['data'] == chatterbox_called_params


@pytest.mark.config(TVM_ENABLED=True)
async def test_tags_not_authorized(support_info_client):
    response = await support_info_client.get(
        '/v1/tags/driver/vasya',
        headers={'Content-Type': 'application/json; charset=utf-8'},
    )
    assert response.status == 403
    # utils.reformat_response made it
    assert await response.json() == {
        'error': (
            '{"status": "error", "message": "TVM header missing", '
            '"code": "tvm-auth-error"}'
        ),
        'status': 'error',
    }


async def test_tags_bad_user_url(support_info_client):
    response = await support_info_client.get(
        '/v1/tags/not_defined_user/23123',
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    # swagger found error
    assert response.status == 400
    assert await response.json() == {
        'status': 'error',
        'message': (
            '\'method\':\n'
            '    - \'parameters\':\n'
            '        - \'path\':\n'
            '            - \'user\':\n'
            '                - \'enum\':\n'
            '                    - "Invalid value. '
            'not_defined_user is not one of the available options '
            '([\'driver\', \'client\'])"'
        ),
    }


async def test_get_all_tags(
        custom_request, mock_chatterbox_search, mock_zendesk_search,
):
    mock_chatterbox_search.set_response(
        {
            'tasks': [
                {
                    'id': '1',
                    'tags': ['1_tag_chatterbox', '1_tag_chatterbox'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {  # this ticket was exported
                    'id': '2',
                    'tags': ['2_tag_chatterbox'],
                    'zendesk_ticket': 100500,
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': '3',
                    'tags': ['3_tag_chatterbox'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {  # this ticket was exported
                    'id': '4',
                    'tags': ['4_tag_chatterbox'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
        },
    )
    mock_zendesk_search.set_response(
        {
            'results': [
                {
                    'id': 100500,
                    'tags': ['1_tag_zendesk', 'forwarded_from_chatterbox'],
                    'external_id': '2',
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': ['2_tag_zendesk'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'tags': ['3_tag_zendesk'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': 100502,
                    'tags': ['4_tag_zendesk', 'source_chatterbox'],
                    'external_id': '4',
                    'created': ONE_DAY_AGO.isoformat(),
                },
            ],
        },
    )

    custom_request.match_info.update(
        {'user': 'driver', 'identification': 'its_driver_license'},
    )
    values = await tags.fetch_all_tags(
        custom_request,
        'driver_license',
        'its_driver_license',
        'user_phone',
        True,
    )
    values = [tag.name for tag in values]
    assert values == [
        '1_tag_chatterbox',
        '1_tag_chatterbox',
        # without 2_tag_chatterbox
        '3_tag_chatterbox',
        # without 4_tag_chatterbox
        '1_tag_zendesk',
        'forwarded_from_chatterbox',
        '2_tag_zendesk',
        '3_tag_zendesk',
        '4_tag_zendesk',
        'source_chatterbox',
    ]

    mock_chatterbox_search.assert_called()
    mock_zendesk_search.assert_called()


@pytest.mark.config(SUPPORT_INFO_TAG_USE_ZENDESK=False)
async def test_tags_without_zendesk(custom_request, mock_chatterbox_search):
    mock_chatterbox_search.set_response(
        {
            'tasks': [
                {
                    'id': '1',
                    'tags': ['1_day_chatterbox'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': '1',
                    'tags': ['1_year_chatterbox'],
                    'created': ONE_YEAR_AGO.isoformat(),
                },
            ],
        },
    )

    custom_request.match_info.update(
        {'user': 'driver', 'identification': 'its_driver_license'},
    )
    values = await tags.fetch_all_tags(
        custom_request,
        'driver_license',
        'its_driver_license',
        ONE_DAY_AGO.isoformat(),
        True,
    )
    values = [tag.name for tag in values]
    assert values == ['1_day_chatterbox', '1_year_chatterbox']

    mock_chatterbox_search.assert_called()


@pytest.mark.parametrize(
    [
        'match_info',
        'user_api_response',
        'tags_response',
        'field',
        'value',
        'is_driver',
        'expected_tags',
        'expected_user_api_request',
        'expected_tags_url',
        'expected_tags_request',
    ],
    [
        (
            {'user': 'client', 'identification': 'some_user_phone'},
            {
                'items': [
                    {
                        'id': '5b2cae5cb2682a976914c2a5',
                        'phone': 'some_user_phone',
                        'type': 'yandex',
                    },
                    {
                        'id': '5b2cae5cb2682a976914c2a6',
                        'phone': 'some_user_phone',
                        'type': 'yandex',
                    },
                ],
            },
            {
                'entities': [
                    {
                        'id': '5b2cae5cb2682a976914c2a5',
                        'tags': ['some', 'tags'],
                    },
                    {
                        'id': '5b2cae5cb2682a976914c2a6',
                        'tags': ['more', 'tags'],
                    },
                ],
            },
            'user_phone_id',
            '000000000000000000000001',
            False,
            {'tags', 'some', 'more', '1_day_chatterbox', '1_year_chatterbox'},
            {
                'items': [{'phone': '000000000000000000000001'}],
                'primary_replica': False,
            },
            'http://passenger-tags.taxi.dev.yandex.net/v1/match',
            {
                'entities': [
                    {
                        'id': '5b2cae5cb2682a976914c2a5',
                        'type': 'user_phone_id',
                    },
                    {
                        'id': '5b2cae5cb2682a976914c2a6',
                        'type': 'user_phone_id',
                    },
                ],
            },
        ),
        (
            {'user': 'driver', 'identification': 'its_driver_license'},
            None,
            {'tags': ['other', 'tags']},
            'driver_license',
            'its_driver_license',
            True,
            {'other', 'tags', '1_year_chatterbox', '1_day_chatterbox'},
            None,
            'http://driver-tags.taxi.dev.yandex.net/v1/drivers/match/profile',
            {'dbid': 'some_park_id', 'uuid': 'driver_uuid'},
        ),
    ],
)
@pytest.mark.config(
    SUPPORT_INFO_TAG_USE_ZENDESK=False,
    SUPPORT_INFO_FETCH_EXTERNAL_TAGS=True,
    USE_DRIVER_TAGS_FOR_MATCH_PROFILE={'__default__': True},
)
async def test_external_tags(
        custom_request,
        mock_chatterbox_search,
        mock_get_tags,
        mockserver,
        match_info,
        user_api_response,
        tags_response,
        field,
        value,
        is_driver,
        expected_tags,
        expected_user_api_request,
        expected_tags_url,
        expected_tags_request,
):
    mocked_tags = mock_get_tags(
        tags_response, 'driver-tags' if is_driver else 'passenger-tags',
    )

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve_bulk')
    def _mock_user_api(request):
        assert request.json == expected_user_api_request
        return user_api_response

    mock_chatterbox_search.set_response(
        {
            'tasks': [
                {
                    'id': '1',
                    'tags': ['1_day_chatterbox'],
                    'created': ONE_DAY_AGO.isoformat(),
                },
                {
                    'id': '1',
                    'tags': ['1_year_chatterbox'],
                    'created': ONE_YEAR_AGO.isoformat(),
                },
            ],
        },
    )

    custom_request.match_info.update(match_info)
    values = await tags.fetch_all_tags(
        custom_request, field, value, ONE_DAY_AGO.isoformat(), is_driver,
    )
    values = {tag.name for tag in values}
    assert values == expected_tags

    mock_chatterbox_search.assert_called()

    if expected_user_api_request is None:
        assert not _mock_user_api.times_called
    else:
        assert _mock_user_api.times_called

    if expected_tags_request is None:
        assert not mocked_tags.times_called
    else:
        tags_request = mocked_tags.next_call()['request']
        assert tags_request.json == expected_tags_request


@pytest.mark.translations(support_info=TRANSLATIONS)
@pytest.mark.config(
    SUPPORT_INFO_CHATTERBOX_TAGS_SEARCH=False,
    SUPPORT_INFO_FETCH_EXTERNAL_TAGS=True,
    SUPPORT_INFO_TAG_USE_ZENDESK=False,
    SUPPORT_INFO_FETCH_USER_PHONE_PD_ID_TAGS=True,
)
@pytest.mark.parametrize(
    'enabled,user,identification,tags_service,tags_response,'
    'next_tags_response,support_tags_response,expected_result,'
    'expected_user_api_request,expected_tags_requests,'
    'expected_support_tags_requests',
    [
        (
            False,
            'client',
            'some_phone_pd_id',
            'passenger-tags',
            {
                'entities': [
                    {
                        'id': '5b2cae5cb2682a976914c2a5',
                        'tags': ['phone_tag', 'other', 'tags'],
                    },
                ],
            },
            {
                'entities': [
                    {
                        'id': 'some_phone_pd_id',
                        'tags': ['phone_pd_id_tag', 'more', 'tags'],
                    },
                ],
            },
            None,
            {
                'items': [
                    {'number': 0, 'tag': 'some_phone_tag'},
                    {'number': 0, 'tag': 'some_phone_pd_id_tag'},
                ],
                'number_days': 60,
                'status': 'ok',
                'threshold': 3,
            },
            {
                'items': [{'phone': 'some_phone_pd_id'}],
                'primary_replica': False,
            },
            [
                {
                    'entities': [
                        {
                            'id': '5b2cae5cb2682a976914c2a5',
                            'type': 'user_phone_id',
                        },
                        {
                            'id': '5b2cae5cb2682a976914c2a6',
                            'type': 'user_phone_id',
                        },
                    ],
                },
                {
                    'entities': [
                        {
                            'id': 'some_phone_pd_id',
                            'type': 'personal_phone_id',
                        },
                    ],
                },
            ],
            [],
        ),
        (
            True,
            'client',
            'some_phone_pd_id',
            'passenger-tags',
            {
                'entities': [
                    {
                        'id': '5b2cae5cb2682a976914c2a5',
                        'tags': ['phone_tag', 'other', 'tags'],
                    },
                ],
            },
            {
                'entities': [
                    {
                        'id': 'some_phone_pd_id',
                        'tags': ['phone_pd_id_tag', 'more', 'tags'],
                    },
                ],
            },
            {'tags': ['support_tag', 'other_tag']},
            {
                'items': [
                    {'number': 0, 'tag': 'some_phone_tag'},
                    {'number': 0, 'tag': 'some_phone_pd_id_tag'},
                    {'number': 0, 'tag': 'some_support_tag'},
                ],
                'number_days': 60,
                'status': 'ok',
                'threshold': 3,
            },
            {
                'items': [{'phone': 'some_phone_pd_id'}],
                'primary_replica': False,
            },
            [
                {
                    'entities': [
                        {
                            'id': '5b2cae5cb2682a976914c2a5',
                            'type': 'user_phone_id',
                        },
                        {
                            'id': '5b2cae5cb2682a976914c2a6',
                            'type': 'user_phone_id',
                        },
                    ],
                },
                {
                    'entities': [
                        {
                            'id': 'some_phone_pd_id',
                            'type': 'personal_phone_id',
                        },
                    ],
                },
            ],
            [
                {
                    'entities': [
                        {
                            'type': 'user_phone_id',
                            'id': '5b2cae5cb2682a976914c2a5',
                        },
                        {
                            'type': 'user_phone_id',
                            'id': '5b2cae5cb2682a976914c2a6',
                        },
                    ],
                },
            ],
        ),
        (
            False,
            'driver',
            'some_driver_license',
            'driver-tags',
            {'tags': ['driver', 'tags', 'chatterbox_tag_driver_wants_promo']},
            None,
            None,
            {
                'items': [{'number': 0, 'tag': 'выпрашивает промокоды'}],
                'number_days': 60,
                'status': 'ok',
                'threshold': 3,
            },
            None,
            [{'dbid': 'some_park_id', 'uuid': 'other_driver_uuid'}],
            [],
        ),
        (
            True,
            'driver',
            'some_driver_license',
            'driver-tags',
            {'tags': ['driver', 'tags', 'chatterbox_tag_driver_wants_promo']},
            None,
            {'tags': ['other_tag', 'chatterbox_tag_driver_cancels_orders']},
            {
                'items': [
                    {'number': 0, 'tag': 'водитель отменяет заказ'},
                    {'number': 0, 'tag': 'выпрашивает промокоды'},
                ],
                'number_days': 60,
                'status': 'ok',
                'threshold': 3,
            },
            None,
            [{'dbid': 'some_park_id', 'uuid': 'other_driver_uuid'}],
            [{'entities': [{'type': 'udid', 'id': 'some_udid'}]}],
        ),
    ],
)
async def test_support_tags(
        mockserver,
        mock_personal_single_response,
        mock_get_tags,
        mock_support_tags,
        support_info_app,
        support_info_client,
        enabled,
        user,
        identification,
        tags_service,
        tags_response,
        next_tags_response,
        support_tags_response,
        expected_result,
        expected_user_api_request,
        expected_tags_requests,
        expected_support_tags_requests,
):
    support_info_app.config.SUPPORT_INFO_FETCH_SUPPORT_TAGS = enabled
    mock_personal_single_response(identification)
    mocked_tags = mock_get_tags(
        response=tags_response,
        tags_service=tags_service,
        next_response=next_tags_response,
    )
    mocked_support_tags = mock_support_tags(response=support_tags_response)

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve_bulk')
    def _mock_user_api(request):
        assert request.json == expected_user_api_request
        return {
            'items': [
                {
                    'id': '5b2cae5cb2682a976914c2a5',
                    'phone': 'some_user_phone',
                    'type': 'yandex',
                },
                {
                    'id': '5b2cae5cb2682a976914c2a6',
                    'phone': 'some_user_phone',
                    'type': 'yandex',
                },
            ],
        }

    response = await support_info_client.get(
        '/v2/tags/{}/{}'.format(user, identification),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    assert response.status == 200
    assert await response.json() == expected_result
    for expected_request in expected_tags_requests:
        assert mocked_tags.next_call()['request'].json == expected_request
    assert not mocked_tags.has_calls
    for expected_request in expected_support_tags_requests:
        assert (
            mocked_support_tags.next_call()['request'].json == expected_request
        )
    assert not mocked_support_tags.has_calls
