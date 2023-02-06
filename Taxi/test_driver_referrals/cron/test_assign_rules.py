# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
import datetime

import pytest

from driver_referrals.common import db as app_db
from driver_referrals.common import models
from driver_referrals.generated.cron import run_cron
from driver_referrals.jobs import assign_rules
from test_driver_referrals import conftest

DRIVER_PARTNER_SOURCE_YANDEX = 'yandex'
DRIVER_PARTNER_SOURCE_SELFEMPLOYED = 'selfemployed_fns'

PARKS = {
    'p3': {
        'id': 'p3',
        'locale': 'ru',
        'country_id': 'rus',
        'driver_partner_source': 'selfemployed_fns',
    },
    'p7': {
        'id': 'p7',
        'locale': 'ru',
        'country_id': 'rus',
        'driver_partner_source': 'selfemployed_fns',
    },
}


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_assign_rules_no_task(cron_context, patch):
    @patch('driver_referrals.common.db.get_drivers_to_assign_rule')
    def get_drivers_to_assign_rule(*args, **kwargs):
        assert False

    async with conftest.TablesDiffCounts(cron_context):
        await run_cron.main(
            ['driver_referrals.jobs.assign_rules', '-t', '0', '-d'],
        )


@pytest.mark.config(
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [
            {
                'rides': 1,
                'payment': 100,
                'child_promocode': {
                    'series': 'test_series',
                    'days_for_activation': 100,
                },
            },
            {
                'rides': 2,
                'promocode': {
                    'series': 'test_series_2',
                    'days_for_activation': 200,
                },
                'child_promocode': {
                    'series': 'test_series_2',
                    'days_for_activation': 200,
                },
            },
        ],
    },
)
@pytest.mark.config(DRIVER_REFERRALS_ASSIGN_RULES_BY_AGGRLOMERATIONS=['eda'])
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, map_reduce_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_assign_rules(
        cron_context,
        mockserver,
        mock_unique_drivers_retrieve_by_uniques,
        mock_driver_profiles_drivers_profiles,
        mock_fleet_parks_v1_parks_list,
):
    mock_fleet_parks_v1_parks_list(PARKS)
    mock_driver_profiles_drivers_profiles(
        eats_keys={'d8': 8, 'd10': 10, 'd11': 11, 'd12': 12, 'd13': 13},
    )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _dummy_driver_tags_request(*args, **kwargs):
        return mockserver.make_response(
            json={
                'drivers': [
                    {
                        'dbid': '7ad36bc7560449998acbe2c57a75c293',
                        'tags': ['good_tag'],
                        'uuid': '33b3103c290fc45aa1b81e0c7d75d5d1',
                    },
                ],
            },
        )

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        source = (
            'selfemployed_fns' if request.park_id in ('p3', 'p7') else 'yandex'
        )
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': source}],
            'total': 1,
            'offset': 0,
        }

    uniques = [
        {
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'park_driver_profile_id': 'p1_d1',
        },
        {
            'park_id': 'p7',
            'driver_profile_id': 'd7',
            'park_driver_profile_id': 'p7_d7',
        },
    ]

    mock_unique_drivers_retrieve_by_uniques(
        {'p7_d7': uniques, 'p1_d1': uniques},
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        park_id = request.json['query']['park']['id']
        return {
            'driver_profiles': [],
            'parks': [
                {
                    'driver_partner_source': (
                        DRIVER_PARTNER_SOURCE_SELFEMPLOYED
                        if park_id in ('p3', 'p7')
                        else DRIVER_PARTNER_SOURCE_YANDEX
                    ),
                },
            ],
            'total': 1,
            'offset': 0,
        }

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2019-04-19T00:00:00+00:00',
                    'booked_at': '2019-04-19T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia,'
                            ' Moscow, Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    @mockserver.json_handler(
        '/eats-core-logistics/internal-api/v1/courier/profiles/retrieve',
    )
    async def _(request):
        return {
            'profiles': [
                {'id': '12', 'data': {'agglomeration_id': 'br_moscow_adm'}},
            ],
        }

    drivers_to_assign = await app_db.get_drivers_to_assign_rule(cron_context)

    def sort_key(x):
        return len(x[0].driver_id), x[0].driver_id

    assert sorted(drivers_to_assign, key=sort_key) == sorted(
        [
            (
                models.PerformerKey(park_id='p7', driver_id='d7'),
                models.PerformerKey(park_id='p0', driver_id='d1'),
            ),
            (
                models.PerformerKey(park_id='p6', driver_id='d6'),
                models.PerformerKey(park_id='p0', driver_id='d1'),
            ),
            (
                models.PerformerKey(park_id='p5', driver_id='d5'),
                models.PerformerKey(park_id='p0', driver_id='d1'),
            ),
            (
                models.PerformerKey(park_id='p4', driver_id='d4'),
                models.PerformerKey(park_id='p0', driver_id='d1'),
            ),
            (
                models.PerformerKey(park_id='p3', driver_id='d3'),
                models.PerformerKey(park_id='p0', driver_id='d1'),
            ),
            (
                models.PerformerKey(park_id='p0', driver_id='d0'),
                models.PerformerKey(park_id='p0', driver_id='d1'),
            ),
            (
                models.PerformerKey(park_id='p9', driver_id='d9'),
                models.PerformerKey(park_id='p8', driver_id='d8'),
            ),
            (
                models.PerformerKey(park_id='p10', driver_id='d10'),
                models.PerformerKey(park_id='p8', driver_id='d8'),
            ),
            (
                models.PerformerKey(park_id='p11', driver_id='d11'),
                models.PerformerKey(park_id='p8', driver_id='d8'),
            ),
            (
                models.PerformerKey(park_id='p12', driver_id='d12'),
                models.PerformerKey(park_id='p8', driver_id='d8'),
            ),
        ],
        key=sort_key,
    )
    async with conftest.TablesDiffCounts(cron_context, {'notifications': 6}):
        await run_cron.main(
            ['driver_referrals.jobs.assign_rules', '-t', '0', '-d'],
        )

    invites = []
    for promocode in ('ПРОМОКОД1', 'ПРОМОКОД2'):
        invites.extend(
            await app_db.get_driver_invites(cron_context, promocode),
        )

    async with cron_context.pg.master_pool.acquire() as conn:
        invites_profiles = await conn.fetch(
            """SELECT park_id, driver_id, reward_reason
               FROM referral_profiles""",
        )
        reward_reasons = {
            f'{r["park_id"]}_{r["driver_id"]}': r['reward_reason']
            for r in invites_profiles
        }

    invites = {
        f'{r["park_id"]}_{r["driver_id"]}': [
            r['status'],
            r['referree_rides'],
            str(r['finish']) if r['finish'] is not None else None,
            reward_reasons[f'{r["park_id"]}_{r["driver_id"]}'],
        ]
        for r in invites
    }

    assert invites == {
        'p0_d0': [
            'in_progress',
            2,
            '2019-05-04 10:00:00',
            'invited_same_park',
        ],
        'p2_d2': ['in_progress', 4, '2018-01-03 12:00:00', None],
        'p3_d3': [
            'in_progress',
            None,
            '2019-06-09 00:02:00',
            'invited_selfemployed',
        ],
        'p4_d4': ['waiting_for_rule', None, None, None],
        'p5_d5': ['waiting_for_rule', None, None, None],
        'p6_d6': [
            'in_progress',
            2,
            '2019-05-04 10:00:00',
            'invited_other_park',
        ],
        'p7_d7': [
            'in_progress',
            2,
            '2019-05-04 10:00:00',
            'invited_selfemployed_from_park',
        ],
        'p9_d9': ['waiting_for_rule', None, None, None],
        'p10_d10': [
            'in_progress',
            1,
            '2019-05-11 21:00:00',
            'invited_other_park',
        ],
        'p11_d11': ['waiting_for_rule', None, None, None],
        'p12_d12': [
            'in_progress',
            1,
            '2019-05-11 00:00:00',
            'invited_other_park',
        ],
    }


def _order(
        *,
        nearest_zone: str = 'correct_zone',
        tariff_class: str = 'correct_tariff',
        orders_provider: str = 'correct_orders_provider',
        created_at: datetime.datetime = datetime.datetime(2020, 7, 1),
) -> models.Order:
    return models.Order(
        order_id='order_id',
        park_id='park_id',
        driver_id='driver_id',
        nearest_zones=[nearest_zone],
        tariff_class=tariff_class,
        orders_provider=orders_provider,
        created_at=created_at,
        synced_at=created_at,
    )


def _rule(*, reason: str, tag: str = None) -> models.ReferralRule:
    return models.ReferralRule(
        id='rule_id',
        created_at=datetime.datetime(2020, 6, 1),
        start_time=datetime.datetime(2020, 6, 1),
        end_time=datetime.datetime(2020, 8, 1),
        tariff_zones=['correct_zone'],
        currency='RUB',
        referree_days=30,
        tariff_classes=['correct_tariff'],
        orders_provider='correct_orders_provider',
        tag=tag,
        steps=[
            models.Step(
                rides=20,
                rewards=[
                    models.Reward(
                        type=models.RewardType.PAYMENT,
                        reason=reason,
                        amount=1000,
                    ),
                ],
                child_rewards=[],
            ),
        ],
    )


@pytest.mark.parametrize(
    (
        'order',
        'rule',
        'is_invited_selfemployed',
        'parent_tags',
        'is_same_park',
        'response',
    ),
    [
        # INVITED_SELFEMPLOYED
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SELFEMPLOYED),
            True,  # is_invited_selfemployed
            [],  # parent_tags
            False,  # is_same_park
            True,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SELFEMPLOYED),
            True,  # is_invited_selfemployed
            [],  # parent_tags
            True,  # is_same_park
            True,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SELFEMPLOYED),
            False,  # is_invited_selfemployed
            [],  # parent_tags
            True,  # is_same_park
            False,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SELFEMPLOYED),
            False,  # is_invited_selfemployed
            [],  # parent_tags
            False,  # is_same_park
            False,  # response
        ),
        # INVITED_SAME_PARK
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SAME_PARK),
            True,  # is_invited_selfemployed
            [],  # parent_tags
            True,  # is_same_park
            False,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SAME_PARK),
            True,  # is_invited_selfemployed
            [],  # parent_tags
            False,  # is_same_park
            False,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SAME_PARK),
            False,  # is_invited_selfemployed
            [],  # parent_tags
            True,  # is_same_park
            True,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_SAME_PARK),
            False,  # is_invited_selfemployed
            [],  # parent_tags
            False,  # is_same_park
            False,  # response
        ),
        # INVITED_OTHER_PARK
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_OTHER_PARK),
            True,  # is_invited_selfemployed
            [],  # parent_tags
            True,  # is_same_park
            False,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_OTHER_PARK),
            True,  # is_invited_selfemployed
            [],  # parent_tags
            False,  # is_same_park
            False,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_OTHER_PARK),
            False,  # is_invited_selfemployed
            [],  # parent_tags
            True,  # is_same_park
            False,  # response
        ),
        (
            _order(),
            _rule(reason=models.RewardReason.INVITED_OTHER_PARK),
            False,  # is_invited_selfemployed
            [],  # parent_tags
            False,  # is_same_park
            True,  # response
        ),
        (
            _order(),
            _rule(
                reason=models.RewardReason.INVITED_OTHER_PARK,
                tag='rule_tag_1',
            ),
            False,  # is_invited_selfemployed
            ['rule_tag_1', 'different_tag'],  # parent_tags
            False,  # is_same_park
            True,  # response
        ),
        (
            _order(),
            _rule(
                reason=models.RewardReason.INVITED_OTHER_PARK,
                tag='rule_tag_1',
            ),
            False,  # is_invited_selfemployed
            ['different_tag'],  # parent_tags
            False,  # is_same_park
            False,  # response
        ),
    ],
)
def test_is_order_meets_rule(
        order: models.Order,
        rule: models.ReferralRule,
        is_invited_selfemployed: bool,
        parent_tags,
        is_same_park: bool,
        response: bool,
):
    assert response == assign_rules.is_order_meets_rule(
        order,
        rule,
        is_invited_selfemployed=is_invited_selfemployed,
        is_same_park=is_same_park,
        parent_tags=parent_tags,
    )
