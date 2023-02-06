import time

import pytest

from . import common

CHECK_TTL = False  # may flap if True
CACHE_TTL = 2 if CHECK_TTL else 120
HALF_TTL = CACHE_TTL / 2


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'],
    SURGE_CACHE_SETTINGS={
        'ENABLED': True,
        'GEOHASH_SIZE': 7,
        'TTL_SEC': CACHE_TTL,
        'EXT_MAX_TTL_SEC': CACHE_TTL,
        'PROLONG_BY_USER_TTL_SEC': 1,
    },
    # doesn't affect test, just to check that we don't fail in this mode
    SURGE_PIPELINE_EXECUTION={'ENABLE_UNIFIED_STAGE_OUT_LOGGING': False},
)
async def test(taxi_surge_calculator, mockserver):
    candidates_count = 0

    @mockserver.json_handler('/candidates/count-by-categories')
    def count_by_categories(request):  # pylint: disable=W0612
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={
                'reposition': {},
                'generic': {
                    'econom': {
                        'total': candidates_count,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                    'business': {
                        'total': candidates_count,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                },
            },
        )

    user_0 = 'test_usr_1'
    user_1 = 'test_usr_2'

    async def check(total_expected, is_cached_expected, user_id, point_a=None):
        request = {
            'point_a': point_a or [37.583369, 55.778821],
            'classes': ['econom', 'business'],
            'user_id': user_id,
        }
        expected = {
            'zone_id': 'MSK-Yandex HQ',
            'user_layer': 'default',
            'experiment_id': 'a29e6a811131450f9a28337906594207',
            'experiment_name': 'default',
            'experiment_layer': 'default',
            'is_cached': is_cached_expected,
            'classes': [
                {
                    'name': 'econom',
                    'calculation_meta': {
                        'counts': {
                            'total': total_expected,
                            'free': 0,
                            'free_chain': 0,
                            'pins': 0,
                            'radius': 1000,
                        },
                    },
                    'value_raw': 1.0,
                    'surge': {'value': 5.0},
                },
                {
                    'name': 'business',
                    'calculation_meta': {
                        'counts': {
                            'total': total_expected,
                            'free': 0,
                            'free_chain': 0,
                            'pins': 0,
                            'radius': 1000,
                        },
                    },
                    'value_raw': 1.0,
                    'surge': {'value': 11.0},
                },
            ],
            'experiments': [],
            'experiment_errors': [],
        }
        response = await taxi_surge_calculator.post(
            '/v1/calc-surge', json=request,
        )
        assert response.status == 200
        actual = response.json()

        assert len(actual.pop('calculation_id', '')) == 32

        common.sort_data(expected)
        common.sort_data(actual)

        assert actual == expected

    # miss and save
    await check(total_expected=0, is_cached_expected=False, user_id=user_0)
    candidates_count = 1
    # hit and load
    await check(total_expected=0, is_cached_expected=True, user_id=user_0)
    # miss [far point] and save
    await check(
        total_expected=1,
        is_cached_expected=False,
        point_a=[37.698792, 55.729158],
        user_id=user_0,
    )
    if CHECK_TTL:
        candidates_count = 0
        # hit and load
        await check(
            total_expected=1,
            is_cached_expected=True,
            point_a=[37.698792, 55.729158],
            user_id=user_0,
        )
        time.sleep(CACHE_TTL)
        # miss [ttl] and save
        await check(
            total_expected=0,
            is_cached_expected=False,
            point_a=[37.698792, 55.729158],
            user_id=user_0,
        )
        candidates_count = 1

        # test one user prolongation
        # miss, cache update
        await check(total_expected=1, is_cached_expected=False, user_id=user_0)
        candidates_count = 0
        time.sleep(HALF_TTL)
        # hit, prolongation
        await check(total_expected=1, is_cached_expected=True, user_id=user_0)
        time.sleep(HALF_TTL)
        # hit
        await check(total_expected=1, is_cached_expected=True, user_id=user_0)
        time.sleep(HALF_TTL)
        # cache expired
        await check(total_expected=0, is_cached_expected=False, user_id=user_0)

        # test two users double prolongation
        candidates_count = 1
        time.sleep(HALF_TTL)
        # prolongation user_1
        await check(total_expected=0, is_cached_expected=True, user_id=user_0)
        time.sleep(HALF_TTL)
        # prolongation user_2
        await check(total_expected=0, is_cached_expected=True, user_id=user_1)
        time.sleep(HALF_TTL)
        # hit, because of second prolongation
        await check(total_expected=0, is_cached_expected=True, user_id=user_0)
        time.sleep(HALF_TTL)
        # miss
        await check(total_expected=1, is_cached_expected=False, user_id=user_1)

        # test max prolongation time
        candidates_count = 3
        for i in range(3):
            time.sleep(HALF_TTL)
            await check(
                total_expected=1,
                is_cached_expected=True,
                user_id='some_user_{}'.format(i),
            )
        time.sleep(HALF_TTL)
        # total elapsed == 4 * half_ttl == 2 * ttl == ttl + ext_ttl
        # cache should be expired now
        await check(total_expected=3, is_cached_expected=False, user_id=user_0)
