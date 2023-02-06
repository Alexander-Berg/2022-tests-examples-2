# flake8: noqa
# pylint: disable=unused-variable
import datetime
from tests_eats_restapp_marketing import sql

import pytest


@pytest.fixture(name='mock_table_campaigns')
def mock_table_campaigns(pgsql):
    class Context:
        def __init__(self):
            self.cursor = pgsql['eats_restapp_marketing'].cursor()

        def push_campaign(
                self,
                campaign_id: int,
                passport_id: int,
                status: str,
                campaign_type: sql.CampaignType = sql.CampaignType.CPM_BANNER_CAMPAIGN,
        ):
            self.cursor.execute(
                (
                    'INSERT INTO eats_restapp_marketing.campaigns '
                    '(campaign_id, passport_id, status, campaign_type) '
                    'VALUES ({}, {}, \'{}\', \'{}\');'
                ).format(campaign_id, passport_id, status, campaign_type),
            )

        def get_inner_campaign_id(self, campaign_id: int):
            self.cursor.execute(
                'SELECT id '
                'FROM eats_restapp_marketing.campaigns '
                'WHERE campaign_id = {}'.format(campaign_id),
            )
            return list(self.cursor)[0][0]

        def get_campaign_status(self, campaign_id: int):
            self.cursor.execute(
                'SELECT status '
                'FROM eats_restapp_marketing.campaigns '
                'WHERE campaign_id = {}'.format(campaign_id),
            )
            return list(self.cursor)[0][0]

    ctx = Context()
    return ctx


@pytest.fixture(name='mock_table_banners')
def mock_table_banners(pgsql):
    class Context:
        def __init__(self):
            self.cursor = pgsql['eats_restapp_marketing'].cursor()
            self.inner_campaign_id = 1
            self.image = 'image'

        def push_place_banner(
                self,
                place_id: int,
                banner_id=None,
                inner_campaign_id=None,
                image=None,
        ):
            if inner_campaign_id is None:
                inner_campaign_id = self.inner_campaign_id
                self.inner_campaign_id += 1
            if image is None:
                image = self.image
            if banner_id is None:
                banner_id = 'NULL'
            self.cursor.execute(
                (
                    'INSERT INTO eats_restapp_marketing.banners '
                    '(inner_campaign_id, place_id, banner_id, image) '
                    'VALUES ({}, {}, {}, \'{}\');'
                ).format(inner_campaign_id, place_id, banner_id, image),
            )

        def get_banner_by_place_id(self, place_id: int):
            self.cursor.execute(
                'SELECT feeds_admin_id '
                'FROM eats_restapp_marketing.banners '
                'WHERE place_id = {}'.format(place_id),
            )
            return list(self.cursor)[0][0]

    ctx = Context()
    return ctx


@pytest.fixture(name='mock_feeds_admin')
def mock_feeds_admin(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200
            self.create_banner_request = None
            self.banner_id = 'banner_id'

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        def check_create_banner_request(
                self,
                media_id: str,
                campaign_id: str,
                yandex_uid: str,
                banner_id: int,
                place_id: int,
        ):
            expected_request = {
                'service': 'eats-promotions-banner',
                'name': 'direct_banner_id_' + str(banner_id),
                'payload': {
                    'priority': 100,
                    'images': [
                        {
                            'media_id': media_id,
                            'media_type': 'image',
                            'platform': 'mobile',
                            'theme': 'light',
                        },
                        {
                            'media_id': media_id,
                            'media_type': 'image',
                            'platform': 'web',
                            'theme': 'light',
                        },
                        {
                            'media_id': media_id,
                            'media_type': 'image',
                            'platform': 'mobile',
                            'theme': 'dark',
                        },
                        {
                            'media_id': media_id,
                            'media_type': 'image',
                            'platform': 'web',
                            'theme': 'dark',
                        },
                    ],
                    'shortcuts': [],
                    'wide_and_short': [],
                    'advert_settings': {
                        'enabled': True,
                        'direct': {
                            'campaign_id': campaign_id,
                            'yandex_uid': yandex_uid,
                            'banner_id': str(banner_id),
                        },
                    },
                },
                'settings': {
                    'description': 'cpm_banner',
                    'restaurant_ids': [place_id],
                    'recipient_type': 'restaurant',
                },
            }
            for expected_field, field in zip(
                    expected_request, self.create_banner_request.json,
            ):
                if expected_field != field:
                    print('not_expected_result: \n')
                    print(expected_field)
                    print(field)

            return self.create_banner_request.json == expected_request

        @property
        def create_banner_times_called(self) -> int:
            return create_banner.times_called

        @property
        def get_urls_times_called(self) -> int:
            return get_urls.times_called

    ctx = Context()

    @mockserver.json_handler('/feeds-admin/v1/media/get-urls')
    def get_urls(request):
        if ctx.status_code == 200:
            json_response = list()
            for item in request.json['media_ids']:
                json_response.append(
                    {
                        'media_id': item,
                        'media_type': 'image',
                        'media_url': 'http//' + item,
                        'tags': [],
                    },
                )
            return mockserver.make_response(
                status=ctx.status_code, json={'urls': json_response},
            )
        return mockserver.make_response(status=ctx.status_code, json={})

    @mockserver.json_handler('/feeds-admin/v1/eats-promotions/create')
    def create_banner(request):
        if ctx.status_code == 200:
            ctx.create_banner_request = request
            ctx.banner_id = request.json['payload']['advert_settings'][
                'direct'
            ]['banner_id']
            return mockserver.make_response(
                status=ctx.status_code,
                json={'id': ('direct_banner_id_' + ctx.banner_id)},
            )
        return mockserver.make_response(status=ctx.status_code, json={})

    return ctx


@pytest.fixture(name='authorizer_user_access')
def authorizer_user_access(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        @property
        def times_called(self) -> int:
            return access_check.times_called

    ctx = Context()

    @mockserver.handler('/eats-restapp-authorizer/v1/user-access/check')
    def access_check(request):
        return mockserver.make_response(status=ctx.status_code)

    return ctx


@pytest.fixture(name='direct_report_stats')
def direct_report_stats(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200
            self.date_from = None
            self.date_to = None
            self.stats = []

        def set_dates(self, date_from: datetime.date, date_to: datetime.date):
            self.date_from = date_from
            self.date_to = date_to

        def add_click_cost(self, clicks: int, cost: int, date: datetime.date):
            self.stats.append(
                {'clicks': clicks, 'cost': cost, 'date': date.isoformat()},
            )

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        @property
        def times_called(self) -> int:
            return reports.times_called

    ctx = Context()

    @mockserver.handler('/direct/json/v5/reports')
    def reports(request):
        if not ctx.date_from or not ctx.date_to:
            return mockserver.make_response(
                status=500, response='no dates set',
            )

        rows: list = []
        rows.append(
            '"Actual Data ({} - {})"'.format(
                ctx.date_from.isoformat(), ctx.date_to.isoformat(),
            ),
        )
        rows.append('Clicks\tCost\tDate')
        for stat in ctx.stats:
            rows.append(
                '{}\t{}\t{}'.format(
                    stat['clicks'], stat['cost'], stat['date'],
                ),
            )

        rows.append('Total rows: {}'.format(len(ctx.stats)))
        rows.append('')

        return mockserver.make_response(
            status=ctx.status_code, response='\n'.join(rows),
        )

    return ctx
