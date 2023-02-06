import copy

import pytest

# pylint: disable=import-only-modules
from .test_eats import EATS_PLACES

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from shortcuts_admin_plugins.generated_tests import *  # noqa


@pytest.mark.parametrize('test_upsert', [False, True])
@pytest.mark.config(
    SHORTCUTS_ADMIN_YT_MOCK={'use_yt': False, 'eats_places': EATS_PLACES},
)
async def test_periodic_dump(
        taxi_shortcuts_admin, pgsql, taxi_config, test_upsert,
):
    def select_eats_places(_cursor):
        _cursor.execute('SELECT * FROM shortcuts_admin.eats_places')
        return _cursor.fetchall()

    # cursor-like-formatter used for comparing data from DB with expected one
    def cl_format(_list):
        return [tuple(_dict.values()) for _dict in _list]

    response = await taxi_shortcuts_admin.post(
        'service/cron', json={'task_name': 'shortcuts_admin-periodic_dump'},
    )
    assert response.status_code == 200

    cursor = pgsql['shortcuts_admin'].cursor()

    assert select_eats_places(cursor) == cl_format(EATS_PLACES)

    if not test_upsert:
        return

    # insert one additional eats place with existing place_id and overridden
    # city; expect that this new eats place will replace the old one
    new_eats_place = copy.deepcopy(EATS_PLACES[-1])
    new_eats_place['address_city'] = 'Spb'

    taxi_config.set(
        SHORTCUTS_ADMIN_YT_MOCK={
            'use_yt': False,
            'eats_places': [new_eats_place],
        },
    )
    # invalidate caches to override config
    await taxi_shortcuts_admin.invalidate_caches()

    response = await taxi_shortcuts_admin.post(
        'service/cron', json={'task_name': 'shortcuts_admin-periodic_dump'},
    )
    assert response.status_code == 200

    expected_eats_places = EATS_PLACES[:-1] + [new_eats_place]
    assert select_eats_places(cursor) == cl_format(expected_eats_places)
