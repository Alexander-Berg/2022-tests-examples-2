import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_data_barcodes.sql',
    ],
)
async def test_get_nomenclature_products_barcodes(
        taxi_eats_nomenclature, pgsql,
):
    barcodes = get_barcodes(pgsql)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )

    assert response.status == 200

    assert map_response(response.json()) == barcodes


def map_response(json):
    categories = json['categories']
    barcodes = {}
    for category in categories:
        for item in category['items']:
            if 'barcodes' in item:
                for item_barcode in item['barcodes']:
                    barcodes[item_barcode['value']] = item_barcode

    return {
        (p['value'], p.get('type') or None, p.get('weightEncoding') or None)
        for value, p in barcodes.items()
    }


def get_barcodes(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
select
    b.value,
    bt.value barcode_type,
    we.value weight_encoding_type
from eats_nomenclature.product_barcodes pb
join eats_nomenclature.barcodes b
    on b.id = pb.barcode_id
left join eats_nomenclature.barcode_types bt
    on b.barcode_type_id = bt.id
left join eats_nomenclature.barcode_weight_encodings we
    on b.barcode_weight_encoding_id = we.id
order by b.value""",
    )
    return set(cursor)
