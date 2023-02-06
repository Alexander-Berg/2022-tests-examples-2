import copy
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_cargo_corp import utils


FEED_KINDS = ['bar', 'important', 'actual', 'news']
MOCK_DISABLED_RESPONSE = {
    'etag': '',
    'feed': [],
    'has_more': False,
    'polling_delay': 1200,
}


def prepare_info_response(
        is_country_set=True, is_city_set=False, is_registration_finished=False,
):
    result = copy.deepcopy(utils.CORP_CLIENT_INFO)
    if not is_country_set:
        del result['company']['country']
    if is_city_set:
        result['company']['city'] = 'Moscow'
    if is_registration_finished:
        result['registered_ts'] = result['updated_ts']
    return result


def build_feed_item(
        *,
        id_: int,
        created: str = '2021-02-01T12:00:00+0000',
        priority: Optional[int] = None,
):
    item: Dict[str, Any] = {
        'feed_id': f'test_feed_id_{id_}',
        'created': created,
        'request_id': f'request_id_{id_}',
        'payload': {'additionalProperty1': 1},
    }

    if priority is not None:
        item.setdefault('meta', {})['priority'] = priority

    return item


def _get_headers(corp_client_id, yandex_uid):
    return {'X-B2B-Client-Id': corp_client_id, 'X-Yandex-Uid': yandex_uid}


@pytest.fixture(name='get_feed_list')
def _get_feed_list(taxi_cargo_corp):
    async def wrapper(
            feed_kind,
            corp_client_id,
            yandex_uid=utils.YANDEX_UID,
            expected_status=200,
    ):
        response = await taxi_cargo_corp.get(
            '/internal/cargo-corp/v1/client/feed/list',
            headers=_get_headers(corp_client_id, yandex_uid),
            params={'feed_kind': feed_kind},
        )
        assert response.status == expected_status
        return response.json()

    return wrapper


class TestFeedList:
    FEED_KIND = 'actual'
    CORP_CLIENT_ID = utils.CORP_CLIENT_ID

    BASIC_CARGO_CHANNELS = [
        'channel:unregistered',
        'channel:unregistered_card_card',
        'all',
        f'id:{CORP_CLIENT_ID}',
        'country:rus',
    ]

    BASIC_TAXI_CHANNELS = ['all', f'id:{CORP_CLIENT_ID}']

    @pytest.fixture(autouse=True)
    def init(
            self,
            feeds_prepare,
            cargo_corp_card_list,
            cargo_corp_client_info,
            cargo_corp_role_list,
            cargo_fin_debts_state,
    ):
        pass

    @pytest.mark.parametrize(
        'has_company_info, expected_times_called',
        [
            pytest.param(False, 0, id='new corp without info'),
            pytest.param(True, 1, id='corp with info'),
        ],
    )
    async def test_calls_cargo(
            self,
            has_company_info,
            expected_times_called,
            get_feed_list,
            cargo_corp_client_info,
            cargo_corp_card_list,
            cargo_corp_role_list,
            cargo_fin_debts_state,
    ):
        info_response = prepare_info_response(is_country_set=has_company_info)
        cargo_corp_client_info.set_response(response_json=info_response)

        await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)
        assert cargo_corp_client_info.times_called == 1
        assert cargo_corp_card_list.times_called == expected_times_called
        assert cargo_corp_role_list.times_called == expected_times_called
        assert cargo_fin_debts_state.times_called == expected_times_called

    async def test_calls_taxi(
            self,
            get_feed_list,
            cargo_corp_client_info,
            cargo_corp_card_list,
            cargo_corp_role_list,
            get_taxi_corp_contracts,
    ):
        cargo_corp_client_info.set_response_by_code(404)
        for _ in range(2):
            await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)
        assert cargo_corp_client_info.times_called == 2
        assert get_taxi_corp_contracts.times_called == 1
        assert cargo_corp_card_list.times_called == 0
        assert cargo_corp_role_list.times_called == 0

    @pytest.mark.parametrize('feed_kind', FEED_KINDS)
    async def test_kinds(self, feed_kind, get_feed_list):
        await get_feed_list(feed_kind, self.CORP_CLIENT_ID)

    @pytest.mark.parametrize(
        'feeds_status_code, expected_status_code',
        [(200, 200), (304, 200), (404, 500)],
    )
    async def test_statuses(
            self,
            get_feed_list,
            feeds_prepare,
            feeds_status_code,
            expected_status_code,
    ):
        feeds_prepare.set_response_by_code(response_code=feeds_status_code)
        await get_feed_list(
            self.FEED_KIND,
            self.CORP_CLIENT_ID,
            expected_status=expected_status_code,
        )

    async def test_ok_response(self, feeds_prepare, get_feed_list):
        get_feed_list_response = await get_feed_list(
            self.FEED_KIND, self.CORP_CLIENT_ID,
        )

        # handle returns time with zero UTC offset
        expected_json = feeds_prepare.get_response()['json']
        expected_json['feed'][0]['created'] = '2017-04-04T14:22:22+0000'
        assert get_feed_list_response == expected_json

    @pytest.fixture
    def assert_channels(self, feeds_prepare, get_feed_list):
        async def wrapper(expected_channels):
            feeds_prepare.set_expected_channels(expected_channels)
            await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)

        return wrapper

    async def test_taxi(self, assert_channels, cargo_corp_client_info):
        cargo_corp_client_info.set_response_by_code(404)
        await assert_channels(self.BASIC_TAXI_CHANNELS + ['contract:prepaid'])

    @pytest.mark.parametrize(
        'payment_type, expected_channel',
        [
            (None, None),
            ('postpaid', 'contract:postpaid'),
            ('prepaid', 'contract:prepaid'),
        ],
    )
    async def test_taxi_contract_channels(
            self,
            assert_channels,
            cargo_corp_client_info,
            get_taxi_corp_contracts,
            payment_type,
            expected_channel,
    ):
        cargo_corp_client_info.set_response_by_code(404)
        get_taxi_corp_contracts.set_contracts(
            has_contracts=(payment_type is not None),
            payment_type=payment_type,
            is_active=True,
        )
        await assert_channels(
            (self.BASIC_TAXI_CHANNELS + [expected_channel])
            if expected_channel is not None
            else self.BASIC_TAXI_CHANNELS,
        )

    @pytest.mark.parametrize('response_code', [400, 404, 500])
    async def test_taxi_exceptions(
            self,
            assert_channels,
            cargo_corp_client_info,
            get_taxi_corp_contracts,
            response_code,
    ):
        cargo_corp_client_info.set_response_by_code(404)
        get_taxi_corp_contracts.set_response_by_code(response_code)
        await assert_channels(self.BASIC_TAXI_CHANNELS)

    @pytest.mark.parametrize(
        'is_country_set, extra_channels',
        [(False, ['channel:company_info_awaited']), (True, ['country:rus'])],
    )
    async def test_country(
            self,
            assert_channels,
            is_country_set,
            extra_channels,
            cargo_corp_client_info,
    ):
        info_response = prepare_info_response(is_country_set=is_country_set)
        cargo_corp_client_info.set_response(response_json=info_response)
        await assert_channels(extra_channels + self.BASIC_CARGO_CHANNELS[:-1])

    async def test_city(self, assert_channels, cargo_corp_client_info):
        info_response = prepare_info_response(is_city_set=True)
        cargo_corp_client_info.set_response(response_json=info_response)
        await assert_channels(['city:Moscow'] + self.BASIC_CARGO_CHANNELS[:])

    async def test_registered(self, assert_channels, cargo_corp_client_info):
        info_response = prepare_info_response(is_registration_finished=True)
        cargo_corp_client_info.set_response(response_json=info_response)
        await assert_channels(
            ['contract:card'] + self.BASIC_CARGO_CHANNELS[2:],
        )

    async def test_no_cards(self, assert_channels, cargo_corp_card_list):
        cargo_corp_card_list.set_cards([])
        await assert_channels(
            ['channel:card_bound_awaited'] + self.BASIC_CARGO_CHANNELS[:],
        )

    async def test_is_admin(self, assert_channels, cargo_corp_role_list):
        cargo_corp_role_list.set_admin_role()
        await assert_channels(
            [f'id:{utils.CORP_CLIENT_ID};role:{utils.OWNER_ROLE}']
            + self.BASIC_CARGO_CHANNELS[:],
        )

    async def test_fail_roles(self, assert_channels, cargo_corp_role_list):
        cargo_corp_role_list.set_response_by_code(500)
        await assert_channels(self.BASIC_CARGO_CHANNELS)

    async def test_has_debts(self, assert_channels, cargo_fin_debts_state):
        cargo_fin_debts_state.set_ok_default(has_debts=True)
        await assert_channels(
            self.BASIC_CARGO_CHANNELS[:] + ['channel:phoenix_has_debts'],
        )

    async def test_fail_debts(self, assert_channels, cargo_fin_debts_state):
        cargo_fin_debts_state.set_response_by_code(500)
        await assert_channels(self.BASIC_CARGO_CHANNELS)

    async def test_priority_only_sorting(self, feeds_prepare, get_feed_list):
        """
        Checks that feed was sorted by descending 'priority'
        """
        feed = [
            build_feed_item(
                id_=0, created='2021-02-01T12:01:00+0000', priority=1,
            ),
            build_feed_item(
                id_=1, created='2021-02-01T12:00:00+0000', priority=3,
            ),
            build_feed_item(
                id_=2, created='2021-02-01T12:02:00+0000', priority=2,
            ),
        ]

        feeds_prepare.set_feed(feed)

        response = await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)
        assert 'feed' in response
        assert response['feed'] == [feed[1], feed[2], feed[0]]

    async def test_equal_priority_sorting(self, feeds_prepare, get_feed_list):
        """
        Checks that feed was sorted by descending 'created'
        with equal 'priority'
        """
        feed = [
            build_feed_item(
                id_=0, created='2021-02-01T12:01:00+0000', priority=1,
            ),
            build_feed_item(
                id_=1, created='2021-02-01T12:00:00+0000', priority=1,
            ),
            build_feed_item(
                id_=2, created='2021-02-01T12:02:00+0000', priority=1,
            ),
        ]

        feeds_prepare.set_feed(feed)

        response = await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)
        assert 'feed' in response
        assert response['feed'] == [feed[2], feed[0], feed[1]]

    async def test_created_sorting(self, feeds_prepare, get_feed_list):
        """
        Checks that feed was sorted by descending 'created'
        when there was no priority field
        """
        feed = [
            build_feed_item(
                id_=0, created='2021-02-01T12:01:00+0000', priority=None,
            ),
            build_feed_item(
                id_=1, created='2021-02-01T12:00:00+0000', priority=None,
            ),
            build_feed_item(
                id_=2, created='2021-02-01T12:02:00+0000', priority=None,
            ),
        ]

        feeds_prepare.set_feed(feed)

        response = await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)
        assert 'feed' in response
        assert response['feed'] == [feed[2], feed[0], feed[1]]

    async def test_mixing_sorting(self, feeds_prepare, get_feed_list):
        """
        Checks that feed was sorted by descending priority and created
        """
        feed = [
            build_feed_item(
                id_=0, created='2021-02-01T12:03:00+0000', priority=1,
            ),
            build_feed_item(
                id_=1, created='2021-02-01T12:00:00+0000', priority=None,
            ),
            build_feed_item(
                id_=2, created='2021-02-01T12:02:00+0000', priority=None,
            ),
            build_feed_item(
                id_=3, created='2021-02-01T12:02:00+0000', priority=2,
            ),
        ]

        feeds_prepare.set_feed(feed)

        response = await get_feed_list(self.FEED_KIND, self.CORP_CLIENT_ID)
        assert 'feed' in response
        assert response['feed'] == [feed[3], feed[0], feed[2], feed[1]]


class TestFeedListDisabled:
    FEED_KIND = 'actual'
    CORP_CLIENT_ID = utils.CORP_CLIENT_ID

    @pytest.fixture(autouse=True)
    def init(
            self,
            cargo_corp_card_list,
            cargo_corp_role_list,
            cargo_fin_debts_state,
    ):
        pass

    @pytest.fixture
    def assert_mock_response(self, feeds_prepare, get_feed_list):
        async def wrapper():
            get_feed_list_response = await get_feed_list(
                self.FEED_KIND, self.CORP_CLIENT_ID,
            )
            assert feeds_prepare.times_called == 0
            assert get_feed_list_response == MOCK_DISABLED_RESPONSE

        return wrapper

    @pytest.mark.config(
        CARGO_CORP_AVAILABLE_FEED_KINDS={'taxi': [], 'cargo': []},
    )
    async def test_all_disabled(
            self, assert_mock_response, cargo_corp_client_info,
    ):
        await assert_mock_response()
        assert cargo_corp_client_info.times_called == 0

    @pytest.mark.config(
        CARGO_CORP_AVAILABLE_FEED_KINDS={'taxi': FEED_KINDS, 'cargo': []},
    )
    async def test_cargo_disabled(
            self, assert_mock_response, cargo_corp_client_info,
    ):
        await assert_mock_response()
        assert cargo_corp_client_info.times_called == 1

    @pytest.mark.config(
        CARGO_CORP_AVAILABLE_FEED_KINDS={'taxi': [], 'cargo': FEED_KINDS},
    )
    async def test_taxi_disabled(
            self, assert_mock_response, cargo_corp_client_info,
    ):
        cargo_corp_client_info.set_response_by_code(404)
        await assert_mock_response()
        assert cargo_corp_client_info.times_called == 1
