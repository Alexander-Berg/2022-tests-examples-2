import pytest


def get_loads(pgsql, user, date):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        fields = ('user_id', 'date', 'yql_link', 'yql_share_link', 'yql_error')
        cursor.execute(
            f'SELECT {", ".join(fields)} FROM ONLY cache.offers_loads '
            f'WHERE user_id=%s AND table_name=%s',
            (user, date),
        )
        db_result = cursor.fetchall()
        return {field: value for field, value in zip(fields, db_result[0])}


@pytest.mark.parametrize(
    'user_id,  expected',
    [
        (
            'user1',
            [
                {
                    'date': '2021-09-20',
                    'shared_link': 'sharelink1',
                    'status': 'RUNNING',
                },
                {
                    'date': '2021-09-21',
                    'shared_link': 'sharelink6',
                    'status': 'READY',
                },
            ],
        ),
        (
            'user2',
            [
                {
                    'date': '2021-09-21',
                    'shared_link': 'sharelink2',
                    'status': 'RUNNING',
                },
                {
                    'date': '2021-09-22',
                    'shared_link': 'sharelink3',
                    'status': 'RUNNING',
                },
            ],
        ),
        (
            'user3',
            [
                {
                    'date': '2021-09-22',
                    'shared_link': 'sharelink4',
                    'status': 'READY',
                },
                {
                    'date': '2021-09-23',
                    'shared_link': 'sharelink5',
                    'status': 'READY',
                },
            ],
        ),
        ('user4', []),
    ],
    ids=['user1', 'user2', 'user3', 'user4'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
async def test_v1_offers_load_operations(
        taxi_pricing_admin, user_id, expected,
):
    response = await taxi_pricing_admin.get(
        'v1/offers/load-operations', params={'user_id': user_id},
    )
    assert response.status_code == 200
    data = response.json()

    assert data == expected
