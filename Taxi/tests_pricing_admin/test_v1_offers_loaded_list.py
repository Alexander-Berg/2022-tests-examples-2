import pytest


def get_saved_offers(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT offer_id, user_id, table_name, offer_data '
            'FROM ONLY cache.user_offers ',
        )
        db_result = cursor.fetchall()
        fields = [column.name for column in cursor.description]
        return [
            {field: value for field, value in zip(fields, db_res)}
            for db_res in db_result
        ]


@pytest.mark.parametrize(
    'user_id,  date, expected, offers_after',
    [
        (
            'user1',
            None,
            {
                'offers': [
                    {
                        'created': '2022-01-15T12:07:15.470004+00:00',
                        'due': '2022-01-15T12:07:15.289561+00:00',
                        'has_fixed_price': True,
                        'id': 'offer4',
                        'has_decoupling': False,
                        'payment_type': 'cash',
                        'tariff_name': 'moscow4',
                        'waypoints_count': 2,
                    },
                    {
                        'created': '2020-04-19T09:21:00.894708+00:00',
                        'id': 'offer2',
                        'payment_type': 'nature',
                        'tariff_name': 'default_city',
                    },
                    {
                        'created': '2020-04-19T09:21:00.894708+00:00',
                        'id': 'offer1',
                        'payment_type': 'nature',
                        'tariff_name': 'default_city',
                    },
                ],
            },
            'offers_after_01.json',
        ),
        ('user2', None, {'offers': []}, 'offers_after_02.json'),
        (
            'user3',
            None,
            {
                'offers': [
                    {
                        'created': '2022-01-15T12:07:15.470004+00:00',
                        'due': '2022-01-15T12:07:15.289561+00:00',
                        'has_fixed_price': True,
                        'id': 'offer1',
                        'has_decoupling': False,
                        'payment_type': 'cash',
                        'tariff_name': 'moscow1',
                        'waypoints_count': 1,
                    },
                    {
                        'created': '2022-01-15T12:07:15.470004+00:00',
                        'due': '2022-01-15T12:07:15.289561+00:00',
                        'has_fixed_price': True,
                        'id': 'offer2',
                        'has_decoupling': True,
                        'payment_type': 'cash',
                        'tariff_name': 'moscow2',
                        'waypoints_count': 3,
                    },
                    {
                        'created': '2022-01-15T12:07:15.470004+00:00',
                        'due': '2022-01-15T12:07:15.289561+00:00',
                        'has_fixed_price': True,
                        'id': 'offer3',
                        'has_decoupling': False,
                        'payment_type': 'cash',
                        'tariff_name': 'moscow3',
                        'waypoints_count': 2,
                    },
                    {
                        'created': '2022-01-15T12:07:15.470004+00:00',
                        'due': '2022-01-15T12:07:15.289561+00:00',
                        'has_fixed_price': True,
                        'id': 'offer5',
                        'has_decoupling': False,
                        'payment_type': 'cash',
                        'tariff_name': 'moscow5',
                        'waypoints_count': 2,
                    },
                ],
            },
            'offers_after_03.json',
        ),
        (
            'user3',
            '2021-09-23',
            {
                'offers': [
                    {
                        'created': '2022-01-15T12:07:15.470004+00:00',
                        'due': '2022-01-15T12:07:15.289561+00:00',
                        'has_fixed_price': True,
                        'id': 'offer3',
                        'has_decoupling': False,
                        'payment_type': 'cash',
                        'tariff_name': 'moscow3',
                        'waypoints_count': 2,
                    },
                ],
            },
            'offers_after_04.json',
        ),
    ],
    ids=['user1', 'user2', 'user3', 'user3_date'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
@pytest.mark.yt(
    schemas=['yt_backend_variables_schema.yaml'],
    dyn_table_data=['yt_backend_variables.yaml'],
)
@pytest.mark.now('2022-01-27 12:00:00.0000+03')
async def test_v1_offers_loaded_list(
        taxi_pricing_admin,
        user_id,
        expected,
        date,
        yt_apply,
        pgsql,
        load_json,
        offers_after,
):
    params = {'user_id': user_id}
    if date:
        params['date'] = date
    response = await taxi_pricing_admin.get(
        'v1/offers/loaded/list', params=params,
    )
    assert response.status_code == 200
    data = response.json()

    assert data == expected
    assert get_saved_offers(pgsql) == load_json(offers_after)
