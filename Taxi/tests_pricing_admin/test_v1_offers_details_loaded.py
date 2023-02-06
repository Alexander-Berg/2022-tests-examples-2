import pytest


def get_loads(pgsql, offer_id, category):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM ONLY cache.offers_details '
            f'WHERE offer_id=%s AND category=%s',
            (offer_id, category),
        )
        db_result = cursor.fetchall()
        fields = [column.name for column in cursor.description]
        if not db_result:
            return None
        return {field: value for field, value in zip(fields, db_result[0])}


@pytest.mark.parametrize(
    'offer_id, category, response_code',
    [
        ('offerX', 'econom', 404),
        ('offer1', 'econom', 200),
        ('offer3', 'econom', 200),
        ('offer4', 'econom', 200),
        ('offer5', 'econom', 200),
    ],
    ids=['absent', 'loading_static', 'loaded', 'load_error', 'loaded_dynamic'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
@pytest.mark.now('2020-09-23 12:00:00.0000+03')
async def test_v1_offers_details_loaded(
        taxi_pricing_admin, offer_id, category, response_code, load_json,
):

    response = await taxi_pricing_admin.get(
        'v1/offers/details/loaded',
        params={'offer_id': offer_id, 'category': category},
    )
    assert response.status_code == response_code
    if response_code == 200:
        response_data = load_json('{}.json'.format(offer_id))
        assert response_data == response.json()
