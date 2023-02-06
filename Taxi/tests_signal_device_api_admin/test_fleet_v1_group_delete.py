import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/group'


def get_amount_of_groups(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT COUNT(*) FROM signal_device_api.device_groups')
    return list(db)[0][0]


def get_grouped_devices_amounts(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        """
        SELECT
            dg.group_name,
            g.amount
        FROM (
            SELECT group_id, COUNT(*) AS amount
            FROM signal_device_api.park_device_profiles
            GROUP BY group_id
        ) AS g
        LEFT JOIN signal_device_api.device_groups dg
        ON (g.group_id = dg.group_id)
    """,
    )
    return {row[0]: row[1] for row in list(db)}


DEFAULT_GROUP_TO_DEVICES_AMOUNT = {
    'SouthWest': 1,
    'South': 1,
    'SouthWestHam': 2,
    None: 2,
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, group_id, amount_of_groups_deleted, group_to_devices_amount',
    [
        (
            'p2',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            3,
            {'SouthWest': 1, None: 5},
        ),
        (
            'p2',
            '1db9bcc6-982c-46ff-a161-78fa1817be01',
            1,
            {'SouthWest': 1, 'South': 1, None: 4},
        ),
        (
            'p3',
            '12bb68a6-aae3-421d-9119-ca1c14fd4862',
            1,
            DEFAULT_GROUP_TO_DEVICES_AMOUNT,
        ),
        (
            'p1',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            0,
            DEFAULT_GROUP_TO_DEVICES_AMOUNT,
        ),
        (
            'p2',
            'a12168a6-22e3-444d-9933-ba1114fd4862',
            0,
            DEFAULT_GROUP_TO_DEVICES_AMOUNT,
        ),
    ],
)
async def test_group_delete(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        group_id,
        amount_of_groups_deleted,
        group_to_devices_amount,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    dg_rows_amount_before = get_amount_of_groups(pgsql)

    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id}

    response = await taxi_signal_device_api_admin.delete(
        ENDPOINT, json={'group_id': group_id}, headers=headers,
    )

    assert response.status_code == 200, response.text
    assert (
        get_amount_of_groups(pgsql)
        == dg_rows_amount_before - amount_of_groups_deleted
    )
    assert get_grouped_devices_amounts(pgsql) == group_to_devices_amount

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT TRUE '
        'FROM signal_device_api.device_groups '
        f'WHERE (group_id = \'{group_id}\' OR '
        f'(parent_group_id IS NOT NULL AND parent_group_id = \'{group_id}\')) '
        f'AND park_id = \'{park_id}\'',
    )
    assert not list(db)
