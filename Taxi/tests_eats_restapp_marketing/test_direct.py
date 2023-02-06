# pylint: disable=unused-variable
import pytest

# -*- coding: utf-8 -*-
PLACE_NAME_PREFIX = 'Ресторан '


def make_warning_error(code, message='', details='') -> dict:
    result = {'Code': code, 'Message': message, 'Details': details}
    return result


def make_add_result(identificator, warnings=None, errors=None) -> dict:
    result = {
        'result': {
            'AddResults': [
                {'Id': identificator, 'Warnings': warnings, 'Errors': errors},
            ],
        },
    }
    return result  # {"result":{"AddResults":[{"Id":4643312098}]}}


def make_place_info_result(place_id) -> dict:
    result = {
        'is_success': True,
        'payload': {
            'id': place_id,
            'name': 'рога и копыта',
            'menu': [
                {
                    'id': 1,
                    'name': 'бургöры №1',
                    'available': True,
                    'schedule_description': 'at 14:00',
                    'items': [],
                },
                {
                    'id': 2,
                    'name': 'бургöры №1',
                    'available': True,
                    'schedule_description': 'at 00:00',
                    'items': [],
                },
            ],
            'slug': 'slug',
        },
        'meta': {'count': None},
    }
    return result


def make_place_info_cc_result(place_id, country_code) -> dict:
    result = make_place_info_result(place_id)
    result['payload']['country_code'] = country_code
    return result


def make_campaign(
        name='рога и копыта', averagecrc=1000000, weekly_spend_limit=None,
) -> dict:
    averagecpc_json = {'AverageCpc': averagecrc}
    if weekly_spend_limit is not None:
        averagecpc_json['WeeklySpendLimit'] = weekly_spend_limit

    result = {
        'method': 'add',
        'params': {
            'Campaigns': [
                {
                    'Name': 'EDA_2',
                    'StartDate': '2020-12-04',
                    'ClientInfo': PLACE_NAME_PREFIX + name,
                    'ContentPromotionCampaign': {
                        'BiddingStrategy': {
                            'Network': {'BiddingStrategyType': 'SERVING_OFF'},
                            'Search': {
                                'AverageCpc': averagecpc_json,
                                'BiddingStrategyType': 'AVERAGE_CPC',
                            },
                        },
                    },
                },
            ],
        },
    }
    return result


def make_group(campaign, name='EDA') -> dict:
    result = {
        'method': 'add',
        'params': {
            'AdGroups': [
                {
                    'CampaignId': campaign,
                    'ContentPromotionAdGroup': {'PromotedContentType': 'EDA'},
                    'Name': name,
                    'RegionIds': [0],
                },
            ],
        },
    }
    return result


def make_content() -> dict:
    result = {
        'method': 'add',
        'params': {
            'PromotedContent': [
                {
                    'Url': 'https://eda.yandex.ru/restaurant/slug',
                    'Type': 'EDA',
                },
            ],
        },
    }
    return result


def make_keyword(keyword, group_id) -> dict:
    result = {'Keyword': keyword, 'AdGroupId': group_id}
    return result


def make_keywords(keywords) -> dict:
    result = {'method': 'add', 'params': {'Keywords': keywords}}
    return result


def make_ad(group_id, content_id, name='рога и копыта') -> dict:
    result = {
        'method': 'add',
        'params': {
            'Ads': [
                {
                    'AdGroupId': group_id,
                    'ContentPromotionEdaAd': {
                        'PromotedContentId': content_id,
                        'Title': PLACE_NAME_PREFIX + name,
                    },
                },
            ],
        },
    }
    return result


@pytest.mark.now('2020-12-04T02:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
async def test_add_ads_no_advert(stq_runner, testpoint):
    @testpoint('NoAdvert')
    def no_advert(data):
        pass

    await stq_runner.add_ads.call(
        task_id='sample_task',
        kwargs={'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
        expect_fail=False,
    )

    assert no_advert.times_called == 1


async def test_add_ads_no_token(stq_runner, testpoint, pgsql):
    @testpoint('NoToken')
    def no_token(data):
        pass

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        INSERT INTO eats_restapp_marketing.advert
        (updated_at, place_id, averagecpc, is_active)
        VALUES (NOW(),1,100,false);
        """,
    )

    await stq_runner.add_ads.call(
        task_id='sample_task',
        kwargs={'token_id': 1, 'place_id': 1, 'averagecpc': 1000000},
        expect_fail=False,
    )

    assert no_token.times_called == 1


@pytest.mark.now('2020-12-04T02:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, stq_expect, oauth, campaign, campaign_response,'
    'group, group_response, add_keywords, add_keywords_response,'
    'promoted_content, promoted_content_response, add_ads, add_ads_response,'
    'reschedule_count',
    [
        pytest.param(
            {
                'token_id': 1,
                'place_id': 2,
                'averagecpc': 1000000,
                'weekly_spend_limit': 2000000,
            },
            False,
            'Bearer token',
            make_campaign(weekly_spend_limit=2000000),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(12345),
            make_ad(1234, 12345),
            make_add_result(123456),
            0,
            id='happy path with weekly limit',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(12345),
            make_ad(1234, 12345),
            make_add_result(123456),
            0,
            id='happy path',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(123),
            make_group(campaign=123),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(12345),
            make_ad(1234, 12345),
            make_add_result(None),
            1,
            id='no_advert',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(123),
            make_group(campaign=123),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(None),
            {},
            make_add_result(None),
            1,
            id='no_content',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(123),
            make_group(campaign=123),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            1,
            id='no_keywords',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(123),
            make_group(campaign=123),
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            1,
            id='no_group',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            1,
            id='no_campaigh',
        ),
    ],
)
async def test_add_ads(
        stq_runner,
        mockserver,
        pgsql,
        stq_kwargs,
        stq_expect,
        oauth,
        testpoint,
        campaign,
        campaign_response,
        group,
        group_response,
        promoted_content,
        promoted_content_response,
        add_keywords,
        add_keywords_response,
        add_ads,
        add_ads_response,
        reschedule_count,
        mocked_time,
):
    @testpoint('Reschedule')
    def reschedule(data):
        pass

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def campaign_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == campaign
        return mockserver.make_response(status=200, json=campaign_response)

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def adgroups_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == group
        return mockserver.make_response(status=200, json=group_response)

    @mockserver.json_handler('/direct/json/v5/promotedcontent')
    def promotedcontent_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == promoted_content
        return mockserver.make_response(
            status=200, json=promoted_content_response,
        )

    @mockserver.json_handler('/direct/json/v5/keywords')
    def keywords_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == add_keywords
        return mockserver.make_response(status=200, json=add_keywords_response)

    @mockserver.json_handler('/direct/json/v5/ads')
    def ads_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        if request.json['method'] == 'add':
            assert request.json == add_ads
            return mockserver.make_response(status=200, json=add_ads_response)
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/direct-internal/campaigns/language')
    def set_lang_handler(request):
        return mockserver.make_response(
            status=200,
            json={'success': True, 'validation_result': {'errors': []}},
        )

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(stq_kwargs['place_id']),
    )
    def places_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
                    'id': stq_kwargs['place_id'],
                    'email': 'qqq@www.ru',
                    'name': 'рога и копыта',
                    'available': True,
                    'disable_details': {
                        'disable_at': '2020-11-27T11:00:00Z',
                        'available_at': '2020-11-27T11:00:00Z',
                        'last_call_date': '2020-11-27T11:00:00Z',
                        'status': 2,
                        'reason': 35,
                    },
                    'full_address': 'qwerty',
                    'description': 'qwerty good',
                    'currency_code': 'RUB',
                    'menu': [
                        {
                            'id': 1,
                            'name': 'бургöры №1',
                            'available': True,
                            'schedule_description': 'at 14:00',
                            'items': [],
                        },
                    ],
                    'phone_numbers': ['+79999999999'],
                    'show_shipping_time': True,
                    'integration_type': 'native',
                    'slug': 'slug',
                },
                'meta': {'count': None},
            },
        )

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_marketing.advert
        (updated_at, place_id, averagecpc, is_active)
        VALUES (NOW(),{},{},false);""".format(
            stq_kwargs['place_id'], stq_kwargs['averagecpc'],
        ),
    )

    await stq_runner.add_ads.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=stq_expect,
    )

    assert reschedule.times_called == reschedule_count


@pytest.mark.now('2020-12-04T05:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, stq_expect, oauth, campaign, campaign_response,'
    'group, group_response, add_keywords, add_keywords_response,'
    'promoted_content, promoted_content_response, add_ads, add_ads_response,'
    'reschedule_counter, one_more',
    [
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            0,
            True,
            id='one_more_reschedule',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            30,
            False,
            id='stop_rescheduling',
        ),
    ],
)
async def test_stq_rescheduling_is_finite(
        stq_runner,
        mockserver,
        pgsql,
        stq_kwargs,
        stq_expect,
        oauth,
        testpoint,
        campaign,
        campaign_response,
        group,
        group_response,
        promoted_content,
        promoted_content_response,
        add_keywords,
        add_keywords_response,
        add_ads,
        add_ads_response,
        reschedule_counter,
        one_more,
        mocked_time,
):
    @testpoint('Reschedule')
    def reschedule(data):
        return

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def campaign_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == campaign
        return mockserver.make_response(status=200, json=campaign_response)

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def adgroups_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == group
        return mockserver.make_response(status=200, json=group_response)

    @mockserver.json_handler('/direct/json/v5/promotedcontent')
    def promotedcontent_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == promoted_content
        return mockserver.make_response(
            status=200, json=promoted_content_response,
        )

    @mockserver.json_handler('/direct/json/v5/keywords')
    def keywords_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == add_keywords
        return mockserver.make_response(status=200, json=add_keywords_response)

    @mockserver.json_handler('/direct/json/v5/ads')
    def ads_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        if request.json['method'] == 'add':
            assert request.json == add_ads
            return mockserver.make_response(status=200, json=add_ads_response)
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(stq_kwargs['place_id']),
    )
    def places_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
                    'id': stq_kwargs['place_id'],
                    'email': 'qqq@www.ru',
                    'name': 'рога и копыта',
                    'available': True,
                    'disable_details': {
                        'disable_at': '2020-11-27T11:00:00Z',
                        'available_at': '2020-11-27T11:00:00Z',
                        'last_call_date': '2020-11-27T11:00:00Z',
                        'status': 2,
                        'reason': 35,
                    },
                    'full_address': 'qwerty',
                    'description': 'qwerty good',
                    'currency_code': 'RUB',
                    'menu': [
                        {
                            'id': 1,
                            'name': 'burger',
                            'available': True,
                            'schedule_description': 'at 14:00',
                            'items': [],
                        },
                    ],
                    'phone_numbers': ['+79999999999'],
                    'show_shipping_time': True,
                    'integration_type': 'native',
                    'slug': 'slug',
                },
                'meta': {'count': None},
            },
        )

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_marketing.advert
        (updated_at, place_id, averagecpc, is_active)
        VALUES (NOW(),{},{},false);""".format(
            stq_kwargs['place_id'], stq_kwargs['averagecpc'],
        ),
    )

    await stq_runner.add_ads.call(
        task_id='sample_task',
        kwargs=stq_kwargs,
        expect_fail=stq_expect,
        reschedule_counter=reschedule_counter,
    )

    assert reschedule.times_called == one_more


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
@pytest.mark.now('2020-12-04T02:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, stq_expect, oauth, campaign, campaign_response,'
    'group, group_response, add_keywords, add_keywords_response,'
    'promoted_content, promoted_content_response, add_ads, add_ads_response,'
    'json_data, reschedule_count',
    [
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(12345),
            make_ad(1234, 12345),
            make_add_result(123456),
            make_place_info_result(2),
            0,
            id='json data without country code',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(12345),
            make_ad(1234, 12345),
            make_add_result(123456),
            make_place_info_cc_result(2, 'RU'),
            0,
            id='json data with country code RU',
        ),
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            'Bearer token',
            make_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_content(),
            make_add_result(12345),
            make_ad(1234, 12345),
            make_add_result(123456),
            make_place_info_cc_result(2, 'KZ'),
            0,
            id='json data with country code KZ',
        ),
    ],
)
async def test_add_ads_no_country_code(
        stq_runner,
        mockserver,
        pgsql,
        stq_kwargs,
        stq_expect,
        oauth,
        testpoint,
        campaign,
        campaign_response,
        group,
        group_response,
        promoted_content,
        promoted_content_response,
        add_keywords,
        add_keywords_response,
        add_ads,
        add_ads_response,
        json_data,
        reschedule_count,
        mocked_time,
):
    @testpoint('Reschedule')
    def reschedule(data):
        pass

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def campaign_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == campaign
        return mockserver.make_response(status=200, json=campaign_response)

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def adgroups_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == group
        return mockserver.make_response(status=200, json=group_response)

    @mockserver.json_handler('/direct/json/v5/promotedcontent')
    def promotedcontent_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == promoted_content
        return mockserver.make_response(
            status=200, json=promoted_content_response,
        )

    @mockserver.json_handler('/direct/json/v5/keywords')
    def keywords_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == add_keywords
        return mockserver.make_response(status=200, json=add_keywords_response)

    @mockserver.json_handler('/direct/json/v5/ads')
    def ads_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        if request.json['method'] == 'add':
            assert request.json == add_ads
            return mockserver.make_response(status=200, json=add_ads_response)
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/direct-internal/campaigns/language')
    def set_lang_handler(request):
        return mockserver.make_response(
            status=200,
            json={'success': True, 'validation_result': {'errors': []}},
        )

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(stq_kwargs['place_id']),
    )
    def places_handler(request):
        return mockserver.make_response(status=200, json=json_data)

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """INSERT INTO eats_restapp_marketing.advert
        (updated_at, place_id, averagecpc, is_active)
        VALUES (NOW(),{},{},false);""".format(
            stq_kwargs['place_id'], stq_kwargs['averagecpc'],
        ),
    )

    await stq_runner.add_ads.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=stq_expect,
    )

    assert reschedule.times_called == reschedule_count


@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.pgsql('eats_restapp_marketing', files=['test_resume_in_stq.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, stq_expect,reschedule_count',
    [
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            1,
            id='resume error',
        ),
    ],
)
async def test_add_ads_resume_error(
        stq_runner,
        mockserver,
        pgsql,
        testpoint,
        mock_eats_advert_resume_error,
        mock_places_handle,
        stq_kwargs,
        stq_expect,
        reschedule_count,
):
    @testpoint('Reschedule')
    def reschedule(data):
        pass

    await stq_runner.add_ads.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=stq_expect,
    )

    assert reschedule.times_called == reschedule_count

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        SELECT is_active
        FROM eats_restapp_marketing.advert
        WHERE place_id = {}
        """.format(
            stq_kwargs['place_id'],
        ),
    )
    assert not list(cursor)[0][0]


@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.pgsql('eats_restapp_marketing', files=['test_resume_in_stq.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, stq_expect,reschedule_count',
    [
        pytest.param(
            {'token_id': 1, 'place_id': 2, 'averagecpc': 1000000},
            False,
            0,
            id='happy path',
        ),
    ],
)
async def test_add_ads_resume_campaign(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_advert_resume,
        mock_places_handle,
        stq_kwargs,
        stq_expect,
        reschedule_count,
):
    @testpoint('Reschedule')
    def reschedule(data):
        pass

    await stq_runner.add_ads.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=stq_expect,
    )

    assert reschedule.times_called == reschedule_count

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        SELECT is_active
        FROM eats_restapp_marketing.advert
        """,
    )
    for item in cursor:
        assert item[0] is True
