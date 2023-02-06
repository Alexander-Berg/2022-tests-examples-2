import datetime
import typing

from dateutil import parser
import pytest
import pytz

from tests_eats_restapp_marketing import direct
from tests_eats_restapp_marketing import experiments
from tests_eats_restapp_marketing import sql


PLACE_NAME_PREFIX = 'Ресторан '
PASSPORT_ID = 1
UTC = datetime.timezone.utc


@pytest.fixture(name='eats_core_places')
def _eats_core_places(mockserver):
    class Context:
        def __init__(self):
            self.place_id = 1
            self.status_code = 200

        def set_place_id(self, place_id: int) -> None:
            self.place_id = place_id

        def set_status_code(self, status_code: int) -> None:
            self.status_code = status_code

        @property
        def times_called(self) -> int:
            return handler.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-core/v1/places/' + str(ctx.place_id))
    def handler(request):
        return mockserver.make_response(
            status=ctx.status_code,
            json={
                'is_success': True,
                'payload': {
                    'id': ctx.place_id,
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

    return ctx


def make_add_result(
        identificator: typing.Optional[int], warnings=None, errors=None,
) -> dict:
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
        name='1', start_date: datetime.date = datetime.date(2020, 12, 4),
) -> dict:

    result = {
        'method': 'add',
        'params': {
            'Campaigns': [
                {
                    'Name': 'EDA_1',
                    'StartDate': start_date.isoformat(),
                    'ClientInfo': name,
                    'CpmBannerCampaign': {
                        'BiddingStrategy': {
                            'Network': {
                                'BiddingStrategyType': (
                                    'WB_MAXIMUM_IMPRESSIONS'
                                ),
                                'WbMaximumImpressions': {
                                    'AverageCpm': 2000000,
                                    'SpendLimit': 100000000,
                                },
                            },
                            'Search': {'BiddingStrategyType': 'SERVING_OFF'},
                        },
                    },
                },
            ],
        },
    }
    return result


def make_cp_campaign(
        name='1',
        start_date: datetime.date = datetime.date(2020, 12, 4),
        end_date: datetime.date = datetime.date(2021, 1, 3),
) -> dict:

    result = {
        'method': 'add',
        'params': {
            'Campaigns': [
                {
                    'Name': 'EDA_1',
                    'StartDate': start_date.isoformat(),
                    'ClientInfo': name,
                    'CpmBannerCampaign': {
                        'BiddingStrategy': {
                            'Network': {
                                'BiddingStrategyType': (
                                    'CP_MAXIMUM_IMPRESSIONS'
                                ),
                                'CpMaximumImpressions': {
                                    'AverageCpm': 2000000,
                                    'SpendLimit': 100000000,
                                    'StartDate': start_date.isoformat(),
                                    'EndDate': end_date.isoformat(),
                                    'AutoContinue': 'NO',
                                },
                            },
                            'Search': {'BiddingStrategyType': 'SERVING_OFF'},
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
                    'CpmBannerKeywordsAdGroup': {},
                    'Name': name,
                    'RegionIds': [0],
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


def make_ad(group_id) -> dict:
    result = {
        'method': 'add',
        'params': {
            'Ads': [
                {
                    'AdGroupId': group_id,
                    'CpmBannerAdBuilderAd': {
                        'Creative': {'CreativeId': 111},
                        'Href': 'https://eda.yandex.ru/restaurant/',
                    },
                },
            ],
        },
    }
    return result


def make_parameters(
        strat_type: str,
        start_date: datetime.datetime = datetime.datetime(
            2020, 12, 3, 0, 0, 0, tzinfo=UTC,
        ),
        end_date: datetime.datetime = datetime.datetime(
            2021, 1, 3, 0, 0, 0, tzinfo=UTC,
        ),
) -> dict:
    typ = (
        'kWbMaximumImpressions'
        if strat_type == 'wb'
        else 'kCpMaximumImpressions'
    )

    return {
        'averagecpm': 2.0,
        'spend_limit': 100.0,
        'strategy_type': typ,
        'start_date': start_date.isoformat('T'),
        'finish_date': end_date.isoformat('T'),
    }


@experiments.add_banner_ads()
@pytest.mark.now('2020-12-04T02:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'stq_kwargs, stq_expect, oauth, campaign, campaign_response,'
    'group, group_response, add_keywords, add_keywords_response,'
    'add_ads, add_ads_response, reschedule_count',
    [
        pytest.param(
            {'token_id': 1, 'inner_campaign_id': '1'},
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
            make_ad(1234),
            make_add_result(123456),
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        passport_id=PASSPORT_ID,
                        parameters=make_parameters('wb'),
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(id=1, inner_campaign_id='1', place_id=1),
                ),
            ),
            id='happy path',
        ),
        pytest.param(
            {'token_id': 1, 'inner_campaign_id': '1'},
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
            make_ad(1234),
            make_add_result(None),
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        passport_id=PASSPORT_ID,
                        parameters=make_parameters('wb'),
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(id=1, inner_campaign_id='1', place_id=1),
                ),
            ),
            id='no_keywords',
        ),
        pytest.param(
            {'token_id': 1, 'inner_campaign_id': '1'},
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
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        passport_id=PASSPORT_ID,
                        parameters=make_parameters('wb'),
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(id=1, inner_campaign_id='1', place_id=1),
                ),
            ),
            id='no_campaign',
        ),
        pytest.param(
            {'token_id': 1, 'inner_campaign_id': '1'},
            False,
            'Bearer token',
            make_cp_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_ad(1234),
            make_add_result(123456),
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        passport_id=PASSPORT_ID,
                        parameters=make_parameters('cp'),
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(id=1, inner_campaign_id='1', place_id=1),
                ),
            ),
            id='happy path cp',
        ),
        pytest.param(
            {'token_id': 1, 'inner_campaign_id': '1'},
            False,
            'Bearer token',
            make_cp_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(None),
            {},
            make_add_result(None),
            {},
            make_add_result(None),
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        passport_id=PASSPORT_ID,
                        parameters=make_parameters('cp'),
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(id=1, inner_campaign_id='1', place_id=1),
                ),
            ),
            id='no group',
        ),
        pytest.param(
            {'token_id': 1, 'inner_campaign_id': '1'},
            False,
            'Bearer token',
            make_cp_campaign(),
            make_add_result(4643312098),
            make_group(campaign=4643312098),
            make_add_result(1234),
            make_keywords(
                [make_keyword('бургры 1', 1234), make_keyword('еда', 1234)],
            ),
            make_add_result(1234567),
            make_ad(1234),
            make_add_result(None),
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        passport_id=PASSPORT_ID,
                        parameters=make_parameters('cp'),
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(id=1, inner_campaign_id='1', place_id=1),
                ),
            ),
            id='no ad',
        ),
    ],
)
async def test_create_cpm_campaign(
        stq_runner,
        mockserver,
        eats_restapp_marketing_db,
        eats_core_places,
        stq_kwargs,
        stq_expect,
        oauth,
        testpoint,
        campaign,
        campaign_response,
        group,
        group_response,
        add_keywords,
        add_keywords_response,
        add_ads,
        add_ads_response,
        reschedule_count,
        mocked_time,
        mock_direct_internal,
        mock_canvas,
):
    @testpoint('Reschedule')
    def reschedule(data):
        pass

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def _campaign_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == campaign
        return mockserver.make_response(status=200, json=campaign_response)

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def _adgroups_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == group
        return mockserver.make_response(status=200, json=group_response)

    @mockserver.json_handler('/direct/json/v5/keywords')
    def _keywords_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        assert request.json == add_keywords
        return mockserver.make_response(status=200, json=add_keywords_response)

    @mockserver.json_handler('/direct/json/v5/ads')
    def _ads_handler(request):
        assert oauth.count('Bearer') == 1
        assert request.headers['Authorization'] == oauth
        if request.json['method'] == 'add':
            assert request.json == add_ads
            return mockserver.make_response(status=200, json=add_ads_response)
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/direct-internal/campaigns/language')
    def _set_lang_handler(request):
        return mockserver.make_response(
            status=200,
            json={'success': True, 'validation_result': {'errors': []}},
        )

    await stq_runner.eats_restapp_marketing_add_banner_ads.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=stq_expect,
    )

    cursor = eats_restapp_marketing_db.cursor()
    cursor.execute(
        """SELECT status
        FROM eats_restapp_marketing.campaigns
        WHERE id = '1'""",
    )
    rows = cursor.fetchall()
    assert rows[0][0] == 'in_creation_process'

    cursor = eats_restapp_marketing_db.cursor()
    cursor.execute(
        """SELECT status
        FROM eats_restapp_marketing.banners
        WHERE id = 1""",
    )
    rows = cursor.fetchall()
    assert rows[0][0] == 'uploaded'

    assert reschedule.times_called == reschedule_count


START_DATE = (
    parser.parse('2022-05-04T12:00:00+03:00').astimezone(pytz.UTC).isoformat()
)
FINISH_DATE = (
    parser.parse('2022-06-04T12:00:00+03:00').astimezone(pytz.UTC).isoformat()
)
PARAM_TEST = {
    'averagecpm': 2,
    'spend_limit': 100,
    'strategy_type': 'kWbMaximumImpressions',
    'start_date': START_DATE,
    'finish_date': FINISH_DATE,
}


@experiments.add_banner_ads()
@pytest.mark.now('2022-06-08T17:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'ads_handler_times_called,direct_calls,campaign',
    [
        pytest.param(
            1,
            1,
            sql.Campaign(
                id='1', passport_id=PASSPORT_ID, parameters=PARAM_TEST,
            ),
            id='no config at all',
        ),
        pytest.param(
            1,
            1,
            sql.Campaign(
                id='1', passport_id=PASSPORT_ID, parameters=PARAM_TEST,
            ),
            marks=experiments.send_ads_to_direct_moderation(False),
            id='disabled config',
        ),
        pytest.param(
            2,
            1,
            sql.Campaign(
                id='1', passport_id=PASSPORT_ID, parameters=PARAM_TEST,
            ),
            marks=experiments.send_ads_to_direct_moderation(True),
            id='enabled config',
        ),
        pytest.param(
            1,
            0,
            sql.Campaign(
                id='1',
                passport_id=PASSPORT_ID,
                parameters=PARAM_TEST,
                status=sql.CampaignStatus.UPDATING,
            ),
            id='updating status',
        ),
        pytest.param(
            1,
            0,
            sql.Campaign(id='1', passport_id=PASSPORT_ID, parameters=None),
            id='no parameters',
        ),
    ],
)
async def test_stq_create_cpm_campaings_moderation(
        stq_runner,
        eats_restapp_marketing_db,
        mockserver,
        mock_direct_campaigns,
        mock_direct_internal,
        eats_core_places,
        mock_canvas,
        ads_handler_times_called,
        campaign,
        direct_calls,
):
    """
    EDACAT-2937: тест проверяет, что при наличие эксперимента в модерацию
    отправляются созданные РК.
    """
    sql.insert_campaign(eats_restapp_marketing_db, campaign)
    sql.insert_banner(
        eats_restapp_marketing_db,
        sql.Banner(id=1, inner_campaign_id='1', place_id=1),
    )

    campaign_id = 1
    group_id = 2
    keyword_id = 3
    ad_id = 4

    mock_direct_campaigns.add_result(direct.IdResult(id=campaign_id))

    @mockserver.json_handler('/direct-internal/campaigns/language')
    def set_lang_handler(request):
        return mockserver.make_response(
            status=200,
            json={'success': True, 'validation_result': {'errors': []}},
        )

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def adgroups_handler(request):
        return mockserver.make_response(
            status=200, json=make_add_result(group_id),
        )

    @mockserver.json_handler('/direct/json/v5/keywords')
    def keywords_handler(request):
        return mockserver.make_response(
            status=200, json=make_add_result(keyword_id),
        )

    @mockserver.json_handler('/direct/json/v5/ads')
    def ads_handler(request):
        return mockserver.make_response(
            status=200, json=make_add_result(ad_id),
        )

    await stq_runner.eats_restapp_marketing_add_banner_ads.call(
        task_id='testsuite/create_cpm_ads',
        kwargs={'token_id': 1, 'inner_campaign_id': '1'},
        expect_fail=False,
    )
    assert mock_direct_campaigns.times_called == direct_calls
    if direct_calls:
        assert set_lang_handler.times_called == 1
        assert adgroups_handler.times_called == 1
        assert keywords_handler.times_called == 1
        assert ads_handler.times_called == ads_handler_times_called

        campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
        assert len(campaigns) == 1

        campaign = campaigns.pop(0)
        assert campaign.campaign_id == campaign_id

        banners = sql.get_all_banners(eats_restapp_marketing_db)
        assert len(banners) == 1

        banner = banners.pop(0)
        assert banner.group_id == group_id
        assert banner.ad_id == ad_id


@experiments.add_banner_ads()
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'start, end, start_date, end_date',
    [
        pytest.param(
            datetime.datetime(2022, 6, 29, 12, 30, 0, tzinfo=UTC),
            datetime.datetime(2022, 7, 29, 12, 30, 0, tzinfo=UTC),
            datetime.date(2022, 6, 29),
            datetime.date(2022, 7, 29),
            marks=pytest.mark.now('2022-05-01T12:00:00+03:00'),
            id='now is earlier than start date',
        ),
        pytest.param(
            datetime.datetime(2022, 6, 29, 12, 30, 0, tzinfo=UTC),
            datetime.datetime(2022, 7, 29, 12, 30, 0, tzinfo=UTC),
            datetime.date(2022, 7, 5),
            datetime.date(2022, 7, 29),
            marks=pytest.mark.now('2022-07-05T12:00:00+03:00'),
            id='now is later than start date',
        ),
        pytest.param(
            datetime.datetime(2022, 6, 29, 12, 30, 0, tzinfo=UTC),
            datetime.datetime(2022, 7, 29, 12, 30, 0, tzinfo=UTC),
            datetime.date(2022, 8, 5),
            datetime.date(2022, 9, 4),
            marks=pytest.mark.now('2022-08-05T12:00:00+03:00'),
            id='now is later than end date; using delta',
        ),
    ],
)
async def test_create_cpm_campaign_dates(
        stq_runner,
        eats_restapp_marketing_db,
        mock_direct_campaigns,
        mockserver,
        mock_direct_internal,
        eats_core_places,
        mock_canvas,
        start: datetime.datetime,
        end: datetime.datetime,
        start_date: datetime.date,
        end_date: datetime.date,
):
    """
    EDACAT-3006: тест проверяет, что в Директ отправляется правильная дата
    начала кампании.
    """

    sql.insert_campaign(
        eats_restapp_marketing_db,
        sql.Campaign(
            id='1',
            passport_id=PASSPORT_ID,
            parameters={
                'averagecpm': 2.0,
                'spend_limit': 100.0,
                'strategy_type': 'kCpMaximumImpressions',
                'start_date': start.isoformat('T'),
                'finish_date': end.isoformat('T'),
            },
        ),
    )
    sql.insert_banner(
        eats_restapp_marketing_db,
        sql.Banner(id=1, inner_campaign_id='1', place_id=1),
    )

    campaign_id = 1
    group_id = 2
    keyword_id = 3
    ad_id = 4

    mock_direct_campaigns.add_result(direct.IdResult(id=campaign_id))

    @mockserver.json_handler('/direct-internal/campaigns/language')
    def set_lang_handler(_):
        return mockserver.make_response(
            status=200,
            json={'success': True, 'validation_result': {'errors': []}},
        )

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def adgroups_handler(_):
        return mockserver.make_response(
            status=200, json=make_add_result(group_id),
        )

    @mockserver.json_handler('/direct/json/v5/keywords')
    def keywords_handler(_):
        return mockserver.make_response(
            status=200, json=make_add_result(keyword_id),
        )

    @mockserver.json_handler('/direct/json/v5/ads')
    def ads_handler(_):
        return mockserver.make_response(
            status=200, json=make_add_result(ad_id),
        )

    await stq_runner.eats_restapp_marketing_add_banner_ads.call(
        task_id='testsuite/create_cpm_ads',
        kwargs={'token_id': 1, 'inner_campaign_id': '1'},
        expect_fail=False,
    )

    assert mock_direct_campaigns.times_called == 1
    assert set_lang_handler.times_called == 1
    assert adgroups_handler.times_called == 1
    assert keywords_handler.times_called == 1
    assert ads_handler.times_called == 1


@pytest.mark.now('2022-07-06T15:00:00+0300')
@pytest.mark.pgsql('eats_tokens', files=['insert_token.sql'])
@pytest.mark.parametrize(
    'tags_requests, group_tags, new_tags',
    [
        pytest.param(
            0,
            [],
            [],
            marks=experiments.add_banner_ads(),
            id='tagging disabled by default',
        ),
        pytest.param(
            1,
            [],
            [],
            marks=experiments.add_banner_ads(
                experiments.AddBannerAds(
                    experiments.GroupTagging(enabled=True),
                ),
            ),
            id='no tags to set',
        ),
        pytest.param(
            1,
            ['testsuite'],
            [],
            marks=experiments.add_banner_ads(
                experiments.AddBannerAds(
                    experiments.GroupTagging(enabled=True, tags=['testsuite']),
                ),
            ),
            id='no new tags to set',
        ),
        pytest.param(
            2,
            [],
            ['testsuite'],
            marks=experiments.add_banner_ads(
                experiments.AddBannerAds(
                    experiments.GroupTagging(enabled=True, tags=['testsuite']),
                ),
            ),
            id='single tag to set',
        ),
        pytest.param(
            2,
            ['a', 'b', 'c'],
            ['d', 'e'],
            marks=experiments.add_banner_ads(
                experiments.AddBannerAds(
                    experiments.GroupTagging(
                        enabled=True, tags=['e', 'b', 'd'],
                    ),
                ),
            ),
            id='single tag to set',
        ),
    ],
)
async def test_stq_create_cpm_campaings_set_group_tags(
        stq_runner,
        eats_restapp_marketing_db,
        mockserver,
        mock_direct_internal,
        mock_direct_campaigns,
        eats_core_places,
        mock_canvas,
        mock_direct_internal_tags,
        tags_requests: int,
        group_tags: typing.List[str],
        new_tags: typing.List[str],
):
    """
    EDACAT-3037: тест проверяет, что есть запрос на проставление тегов группе
    объявлений в случае включенного конфига.
    """

    sql.insert_campaign(
        eats_restapp_marketing_db,
        sql.Campaign(id='1', passport_id=PASSPORT_ID, parameters=PARAM_TEST),
    )
    sql.insert_banner(
        eats_restapp_marketing_db,
        sql.Banner(id=1, inner_campaign_id='1', place_id=1),
    )

    campaign_id = 1
    group_id = 2
    keyword_id = 3
    ad_id = 4

    mock_direct_campaigns.add_result(direct.IdResult(id=campaign_id))

    mock_direct_internal_tags.set_tags(group_tags)

    @mock_direct_internal_tags.request_assertion
    def _check_request_tags(request):
        assert group_id in request.json['ad_group_ids']

        if 'bs_tags' not in request.json:
            return

        bs_tags = request.json['bs_tags']
        assert sorted(bs_tags) == sorted(new_tags)

    @mockserver.json_handler('/direct-internal/campaigns/language')
    def set_lang_handler(_):
        return mockserver.make_response(
            status=200,
            json={'success': True, 'validation_result': {'errors': []}},
        )

    @mockserver.json_handler('/direct/json/v5/adgroups')
    def adgroups_handler(_):
        return mockserver.make_response(
            status=200, json=make_add_result(group_id),
        )

    @mockserver.json_handler('/direct/json/v5/keywords')
    def keywords_handler(_):
        return mockserver.make_response(
            status=200, json=make_add_result(keyword_id),
        )

    @mockserver.json_handler('/direct/json/v5/ads')
    def ads_handler(_):
        return mockserver.make_response(
            status=200, json=make_add_result(ad_id),
        )

    await stq_runner.eats_restapp_marketing_add_banner_ads.call(
        task_id='testsuite/create_cpm_ads',
        kwargs={'token_id': 1, 'inner_campaign_id': '1'},
        expect_fail=False,
    )

    assert set_lang_handler.times_called == 1
    assert adgroups_handler.times_called == 1
    assert keywords_handler.times_called == 1
    assert ads_handler.times_called == 1
    assert mock_direct_internal_tags.times_called == tags_requests

    campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert len(campaigns) == 1

    campaign = campaigns.pop(0)
    assert campaign.campaign_id == campaign_id

    banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert len(banners) == 1

    banner = banners.pop(0)
    assert banner.group_id == group_id
    assert banner.ad_id == ad_id
