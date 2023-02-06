from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_ride_discounts import common

PATH_ADD_RULES = '/v1/admin/match-discounts/add-rules'
PATH_HANDLER = '/v1/match-discounts/available-by-zone'

GEO_NODES = [
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'agglomeration',
        'parent_name': 'br_moskovskaja_obl',
    },
    {
        'name': 'br_moscow_adm',
        'name_en': 'Moscow (adm)',
        'name_ru': 'Москва (адм)',
        'node_type': 'node',
        'parent_name': 'br_moscow',
        'tariff_zones': ['moscow'],
        'region_id': '213',
    },
    {
        'name': 'br_moscow_middle_region',
        'name_en': 'Moscow (Middle Region)',
        'name_ru': 'Москва (среднее)',
        'node_type': 'node',
        'parent_name': 'br_moscow',
    },
    {
        'name': 'br_moskovskaja_obl',
        'node_type': 'node',
        'name_en': 'Moscow Region',
        'name_ru': 'Московская область',
        'parent_name': 'br_tsentralnyj_fo',
        'region_id': '1',
    },
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'country',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_tsentralnyj_fo',
        'name_en': 'Central Federal District',
        'name_ru': 'Центральный ФО',
        'node_type': 'node',
        'parent_name': 'br_russia',
        'region_id': '3',
    },
]


def _get_add_rules_json(
        discount_has_yaplus: Optional[List[int]] = None,
        discount_tariff_zone: str = 'moscow',
        **settings,
) -> Dict[str, Any]:
    discount_tariff = settings.get('discount_tariff', ['econom'])
    add_rules_json: Dict[str, Any] = {
        'series_id': '78563307-7501-42c2-9468-e63f727ddaa4',
        'affected_discount_ids': [],
        'data': {
            'discount': common.make_discount(
                hierarchy_name='experimental_money_discounts',
            ),
            'hierarchy_name': 'experimental_money_discounts',
        },
        'rules': [
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'end': '2021-07-08T15:00:00+00:00',
                        'is_end_utc': True,
                        'is_start_utc': True,
                        'start': '2021-06-25T18:00:00+00:00',
                    },
                ],
            },
            {
                'condition_name': 'zone',
                'values': [
                    {
                        'is_prioritized': False,
                        'name': discount_tariff_zone,
                        'type': 'tariff_zone',
                    },
                ],
            },
            {'condition_name': 'tariff', 'values': discount_tariff},
        ],
    }
    if discount_has_yaplus is not None:
        add_rules_json['rules'].append(
            {'condition_name': 'has_yaplus', 'values': discount_has_yaplus},
        )
    return add_rules_json


async def _add_rules_request(client, add_rules_json: Dict[str, Any]):
    """
    To search for any discount, you should first add it.
    """
    response = await client.post(
        PATH_ADD_RULES,
        headers=common.get_draft_headers(),
        json=add_rules_json,
    )
    return response


def _add_rules_response_checking(response) -> None:
    """
    Formal verification that the discount was added successfully.
    Otherwise, we have a chance to get the correct result of a broken search,
    with an expected empty answer.
    """
    assert response.status_code == 200


async def _available_request(
        client,
        needle_has_yaplus: Optional[bool] = None,
        needle_tariff_zone: str = 'moscow',
        needle_request_time: str = '2021-06-26T18:00:00+00:00',
        **settings,
):
    """
    We make a request to check the availability
    of a discount on the substituted parameters.
    """
    needle_tariffs = settings.get('needle_tariffs', ['econom'])
    available_json: Dict[str, Any] = {
        'request_time': needle_request_time,
        'client_timezone': 'Europe/Moscow',
        'tariffs': needle_tariffs,
        'tariff_zone': needle_tariff_zone,
    }
    if needle_has_yaplus is not None:
        available_json['has_yaplus'] = needle_has_yaplus
    response = await client.post(
        PATH_HANDLER, headers=common.get_headers(), json=available_json,
    )
    return response


def _available_response_checking(
        response, excepted_tariffs_availability: List[str],
) -> None:
    """
    Checking the availability response.
    Discounted rates can be issued in an arbitrary, not sorted order.
    """
    assert response.status_code == 200
    response_json = response.json()
    response_json['tariffs_availability'].sort()
    excepted_tariffs_availability.sort()
    assert response_json == {
        'tariffs_availability': excepted_tariffs_availability,
    }


@pytest.mark.geo_nodes(GEO_NODES)
@pytest.mark.usefixtures('reset_data_id')
async def _main_processing(
        client,
        mocked_time,
        excepted_tariffs_availability: List[str],
        **settings,
) -> None:
    """
    The main node describing the logic of how any test works.
    Any entry point will pass through this function.
    """
    add_rules_json = _get_add_rules_json(**settings)

    response = await _add_rules_request(client, add_rules_json)
    _add_rules_response_checking(response)

    await client.invalidate_caches()

    response = await _available_request(client, **settings)
    _available_response_checking(response, excepted_tariffs_availability)


# Case 1


@pytest.mark.parametrize(
    'discount_has_yaplus',
    (
        pytest.param(None),
        pytest.param([0]),
        pytest.param([1]),
        pytest.param([0, 1]),
    ),
)
@pytest.mark.parametrize(
    'needle_has_yaplus',
    (pytest.param(None), pytest.param(False), pytest.param(True)),
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_yaplus(
        client,
        mocked_time,
        discount_has_yaplus: Optional[List[int]],
        needle_has_yaplus: Optional[bool],
) -> None:
    """
    With the has_yaplus field set to "true",
    the search should find discounts for subscription holders
    and discounts where a subscription is not required.
    """
    d_yaplus = [0, 1] if discount_has_yaplus is None else discount_has_yaplus
    n_yaplus = False if needle_has_yaplus is None else needle_has_yaplus
    await _main_processing(
        client,
        mocked_time,
        [] if n_yaplus not in d_yaplus else ['econom'],
        discount_has_yaplus=discount_has_yaplus,
        needle_has_yaplus=needle_has_yaplus,
    )


# Case 2


@pytest.mark.parametrize(
    'discount_tariff',
    (
        pytest.param(['econom']),
        pytest.param(['comfort']),
        pytest.param(['econom', 'comfort']),
    ),
)
@pytest.mark.parametrize(
    'needle_tariffs',
    (
        pytest.param(['econom']),
        pytest.param(['comfort']),
        pytest.param(['econom', 'comfort']),
    ),
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_tariff(
        client,
        mocked_time,
        discount_tariff: List[str],
        needle_tariffs: List[str],
) -> None:
    """
    Checking for the correct issuance of tariffs.
    Is one of the main fields.
    """
    await _main_processing(
        client,
        mocked_time,
        [tariff for tariff in needle_tariffs if tariff in discount_tariff],
        discount_tariff=discount_tariff,
        needle_tariffs=needle_tariffs,
    )


# Case 3


@pytest.mark.parametrize('discount_tariff_zone', (pytest.param('moscow'),))
@pytest.mark.parametrize(
    'needle_tariff_zone',
    (
        pytest.param('not valid zone'),
        pytest.param('moscow'),
        pytest.param('russia'),
    ),
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_tarriff_zone(
        client,
        mocked_time,
        discount_tariff_zone: str,
        needle_tariff_zone: str,
) -> None:
    """
    Is one of the main fields.
    """
    await _main_processing(
        client,
        mocked_time,
        [] if needle_tariff_zone != 'moscow' else ['econom'],
        discount_tariff_zone=discount_tariff_zone,
        needle_tariff_zone=needle_tariff_zone,
    )


# Case 4


@pytest.mark.parametrize(
    'has_match, needle_request_time',
    (
        pytest.param(False, '2020-06-26T18:00:00+00:00'),
        pytest.param(True, '2021-06-26T18:00:00+00:00'),
        pytest.param(False, '2022-06-26T18:00:00+00:00'),
    ),
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_request_time(
        client, mocked_time, has_match: bool, needle_request_time: str,
) -> None:
    """
    If the discount period is in the future
    or past from the time of the request,
    the discount should not be visible
    """
    await _main_processing(
        client,
        mocked_time,
        ['econom'] if has_match else [],
        needle_request_time=needle_request_time,
    )
