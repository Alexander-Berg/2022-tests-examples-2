import pytest

ENDPOINT = '/internal/driver/v1/operations/create'
FILE_NAME = 'file_name.csv'


async def test_success(taxi_fleet_reports_storage, pgsql):
    response = await taxi_fleet_reports_storage.post(
        ENDPOINT,
        json={
            'id': 'test_operation_00000000000000000',
            'park_id': 'park_id_0',
            'driver_id': '1',
            'name': 'report_vat',
            'file_name': FILE_NAME,
        },
    )

    cursor = pgsql['fleet_reports'].cursor()

    cursor.execute(
        f"""
        SELECT id
        FROM fleet_reports_storage.operations
        WHERE park_id = \'park_id_0\'
        """,
    )

    assert cursor.rowcount == 1
    assert response.status_code == 200


async def test_duplicate(taxi_fleet_reports_storage, pgsql):
    for _i in range(0, 3):
        response = await taxi_fleet_reports_storage.post(
            ENDPOINT,
            json={
                'id': 'base_operation_00000000000000000',
                'park_id': 'park_id_0',
                'driver_id': '1',
                'name': 'report_vat',
                'file_name': FILE_NAME,
            },
        )

        assert response.status_code == 200

    cursor = pgsql['fleet_reports'].cursor()

    cursor.execute(
        f"""
        SELECT count(*)
        FROM fleet_reports_storage.operations
        WHERE id = \'base_operation_00000000000000000\'
        """,
    )

    assert cursor.fetchone()[0] == 1


@pytest.mark.config(
    FLEET_REPORTS_STORAGE_QUOTA={
        'is_enabled': True,
        'all': {'park': 2},
        'default': {'park': 2},
    },
)
async def test_quota(taxi_fleet_reports_storage, pgsql):
    for i in range(0, 4):
        response = await taxi_fleet_reports_storage.post(
            ENDPOINT,
            json={
                'id': 'test_operation_0000000000000000' + str(i),
                'park_id': 'park_id_0',
                'driver_id': '1',
                'name': 'report_vat',
                'file_name': FILE_NAME,
            },
        )

        if i < 2:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

    cursor = pgsql['fleet_reports'].cursor()
    cursor.execute(
        f"""
        SELECT id
        FROM fleet_reports_storage.operations
        WHERE park_id = \'park_id_0\'
        """,
    )
    assert cursor.rowcount == 2
