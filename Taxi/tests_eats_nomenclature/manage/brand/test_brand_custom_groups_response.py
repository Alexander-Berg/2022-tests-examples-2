import pytest


HANDLER = '/v1/manage/brand/custom_categories_groups'
BRAND_ID = 1


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_assortment_name(taxi_eats_nomenclature, load_json):
    unknown_assortment_name = 'UNKNOWN_ASSORTMENT_NAME'
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={unknown_assortment_name}',
        json=load_json('request.json'),
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_brand(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')

    # Request unknown brand_id.
    response = await taxi_eats_nomenclature.post(
        HANDLER + '?brand_id=123', json=request,
    )

    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_custom_groups(taxi_eats_nomenclature, load_json):
    request = load_json('request.json')
    # Add unknown custom groups.
    unknown_custom_groups = [
        {'id': '12345678-7777-7777-7777-777777777777', 'sort_order': 50},
        {'id': '87654321-6666-6666-6666-666666666666'},
    ]
    request['categories_groups'] += unknown_custom_groups

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}', json=request,
    )

    assert response.status_code == 404
    assert set(response.json()['group_ids']) == {
        '12345678-7777-7777-7777-777777777777',
        '87654321-6666-6666-6666-666666666666',
    }
