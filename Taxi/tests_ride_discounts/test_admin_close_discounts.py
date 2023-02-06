import datetime
from typing import Dict
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_ride_discounts import common


async def _close_discounts_check(
        client,
        pgsql,
        hierarchy_name: str,
        discount_ids: List[str],
        closed_at: Optional[datetime.datetime],
        expected_status_code: int,
        expected_response: Optional[dict],
        no_match_expected: bool,
) -> List[str]:
    start_revision = common.get_max_revision(hierarchy_name, pgsql)

    request: dict = {
        'hierarchy_name': hierarchy_name,
        'discount_ids': discount_ids,
        'closed_at': closed_at,
    }

    headers = common.get_headers()
    response = await client.post(
        'v1/admin/match-discounts/close-discounts/check',
        request,
        headers=headers,
    )
    assert response.status_code == expected_status_code, response.json()
    end_revision = common.get_max_revision(hierarchy_name, pgsql)

    response_json = response.json()
    assert end_revision == start_revision
    if expected_status_code != 200:
        if expected_response is not None:
            assert response_json == expected_response
        return []

    response_affected_discount_ids: List[str] = sorted(
        response_json['data']['affected_discount_ids'],
    )
    assert bool(response_affected_discount_ids) != no_match_expected

    response_lock_ids: List[dict] = response_json['lock_ids']
    lock_ids = [
        lock_id['id'].replace('ride-discounts', '')
        for lock_id in response_lock_ids
    ]
    assert sorted(lock_ids) == response_affected_discount_ids
    del response_json['data']['affected_discount_ids']
    del response_json['lock_ids']

    data: dict = {
        'hierarchy_name': hierarchy_name,
        'discount_ids': sorted(discount_ids),
    }
    if closed_at:
        data['closed_at'] = closed_at
    response_json['data']['discount_ids'].sort()
    assert response_json == {'data': data}
    return response_affected_discount_ids


DATA_ID_0 = common.START_DATA_ID
DATA_ID_1 = str(int(DATA_ID_0) + 1)


@pytest.mark.parametrize(
    'add_rules_data, discount_ids, hierarchy_name, close_start_time,'
    'closed_at, expected_status_code, expected_response, no_match_expected',
    (
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 1),
            None,
            200,
            None,
            False,
            id='end_time_equal_to_start_payment_method_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2022, 1, 1),
            None,
            200,
            None,
            False,
            id='end_time_extension_payment_method_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'full_cashback_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'full_cashback_discounts',
            datetime.datetime(2020, 1, 1, 11),
            None,
            200,
            None,
            False,
            id='end_time_before_start_full_money_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 2),
            None,
            200,
            None,
            False,
            id='good_conditions_payment_method_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'experimental_money_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'experimental_money_discounts',
            datetime.datetime(2020, 1, 1, 11),
            None,
            200,
            None,
            False,
            id='end_time_before_start_experimental_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'full_money_discounts'}),
            [DATA_ID_1],
            'full_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 5),
            None,
            200,
            None,
            True,
            id='not_match_discount_ids',
        ),
        pytest.param(
            common.get_add_rules_data({'full_money_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'full_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 5),
            '2020-01-01T12:15:16+00:00',
            200,
            None,
            False,
            id='closed_at_after_start_time',
        ),
        pytest.param(
            common.get_add_rules_data({'full_money_discounts'}),
            [DATA_ID_0, DATA_ID_1],
            'full_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 5),
            '2020-01-01T11:55:16+00:00',
            400,
            None,
            False,
            id='closed_at_after_start_time',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
    APPLICATION_MAP_DISCOUNTS={
        'some_application_name': 'some_application_type',
    },
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    APPLICATION_MAP_PLATFORM={
        'some_application_name': 'some_application_platform',
    },
    APPLICATION_MAP_BRAND={'some_application_name': 'some_application_brand'},
)
async def test_close_discounts_check(
        client,
        pgsql,
        add_rules,
        reset_data_id,
        mocked_time,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        discount_ids: List[str],
        close_start_time: datetime.datetime,
        closed_at: Optional[datetime.datetime],
        expected_status_code: int,
        expected_response: Optional[dict],
        no_match_expected: bool,
):
    await common.init_bin_sets(client)

    await add_rules(add_rules_data)

    mocked_time.set(close_start_time)
    await _close_discounts_check(
        client,
        pgsql,
        hierarchy_name,
        discount_ids,
        closed_at,
        expected_status_code,
        expected_response,
        no_match_expected,
    )
    discount = await common.load_discount(client, DATA_ID_0)
    assert discount and ('end_time_draft_id' not in discount['meta_info'])


@pytest.mark.parametrize(
    'add_rules_data, affected_discount_ids, discount_ids, hierarchy_name,'
    'close_start_time, closed_at, expected_status_code, expected_response,'
    'change_expected, no_match_expected',
    (
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 1),
            None,
            200,
            None,
            True,
            False,
            id='end_time_equal_to_start_payment_method_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2022, 1, 1),
            None,
            200,
            None,
            True,
            False,
            id='end_time_extension_payment_method_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'full_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'full_money_discounts',
            datetime.datetime(2020, 1, 1, 11),
            None,
            200,
            None,
            True,
            False,
            id='end_time_before_start_full_money_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 2),
            None,
            200,
            None,
            True,
            False,
            id='good_conditions_payment_method_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'experimental_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'experimental_money_discounts',
            datetime.datetime(2020, 1, 1, 11),
            None,
            200,
            None,
            True,
            False,
            id='end_time_before_start_experimental_discounts',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            None,
            [DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 5),
            None,
            200,
            None,
            False,
            True,
            id='not_match_conditions',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 1),
            '2020-01-01T12:15:16+00:00',
            200,
            None,
            True,
            False,
            id='closed_at_after_close_start_time',
        ),
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            None,
            [DATA_ID_0, DATA_ID_1],
            'payment_method_money_discounts',
            datetime.datetime(2020, 1, 1, 12, 0, 1),
            '2020-01-01T11:55:16+00:00',
            400,
            None,
            True,
            False,
            id='closed_at_before_close_start_time',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
    APPLICATION_MAP_DISCOUNTS={
        'some_application_name': 'some_application_type',
    },
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    APPLICATION_MAP_PLATFORM={
        'some_application_name': 'some_application_platform',
    },
    APPLICATION_MAP_BRAND={'some_application_name': 'some_application_brand'},
)
async def test_close_discounts(
        client,
        pgsql,
        add_rules,
        reset_data_id,
        mocked_time,
        affected_discount_ids: Optional[List[str]],
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        discount_ids: List[str],
        close_start_time: datetime.datetime,
        closed_at: datetime.datetime,
        expected_status_code: int,
        expected_response: Optional[dict],
        change_expected: bool,
        no_match_expected: bool,
):
    await common.init_bin_sets(client)

    await add_rules(add_rules_data)

    start_revision = common.get_revision(pgsql)

    mocked_time.set(close_start_time)
    if affected_discount_ids is None:
        if expected_status_code == 200:
            affected_discount_ids = await _close_discounts_check(
                client,
                pgsql,
                hierarchy_name,
                discount_ids,
                closed_at,
                200,
                None,
                no_match_expected,
            )
        else:
            await _close_discounts_check(
                client,
                pgsql,
                hierarchy_name,
                discount_ids,
                closed_at,
                expected_status_code,
                expected_response,
                no_match_expected,
            )
            return

    if expected_status_code == 200:
        assert change_expected == bool(affected_discount_ids)
    request: dict = {
        'hierarchy_name': hierarchy_name,
        'discount_ids': discount_ids,
        'affected_discount_ids': affected_discount_ids,
    }
    if closed_at:
        request['closed_at'] = closed_at

    headers = common.get_draft_headers('draft_id_close_discounts')
    response = await client.post(
        'v1/admin/match-discounts/close-discounts', request, headers=headers,
    )
    assert response.status_code == expected_status_code
    end_revision = common.get_revision(pgsql)

    assert end_revision == start_revision

    if expected_status_code != 200:
        if expected_response is not None:
            assert response.json() == expected_response
        return

    assert not response.content

    discount = await common.load_discount(client, DATA_ID_0)
    assert discount and (
        change_expected == ('end_time_draft_id' in discount['meta_info'])
    )


@pytest.mark.parametrize(
    'add_rules_data, discount_ids, hierarchy_name',
    (
        pytest.param(
            common.get_add_rules_data({'payment_method_money_discounts'}),
            ['1', '2'],
            'payment_method_money_discounts',
            id='payment_method_money_discounts',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-12-01T00:00:00+00:00')
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
    APPLICATION_MAP_DISCOUNTS={
        'some_application_name': 'some_application_type',
    },
    DISCOUNTS_MATCH_CLOSE_RULES_SETTINGS={
        '__default__': {'close_after_sec': 10},
    },
    APPLICATION_MAP_PLATFORM={
        'some_application_name': 'some_application_platform',
    },
    APPLICATION_MAP_BRAND={'some_application_name': 'some_application_brand'},
)
async def test_close_discounts_duplicate(
        client,
        pgsql,
        add_rules,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        discount_ids: List[str],
):
    await common.init_bin_sets(client)

    for discount_id in discount_ids:
        await add_rules(add_rules_data)

        request: dict = {
            'hierarchy_name': hierarchy_name,
            'discount_ids': [discount_id],
            'affected_discount_ids': [discount_id],
        }

        headers = common.get_draft_headers(
            'draft_id_close_discounts' + discount_id,
        )
        response = await client.post(
            'v1/admin/match-discounts/close-discounts',
            request,
            headers=headers,
        )
        assert response.status_code == 200

        assert not response.content
