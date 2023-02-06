import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils

ASSORTMENT_ID = 1


@pennies_utils.PARAMETRIZE_PRICE_ROUNDING
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_get_nomenclature_products(
        taxi_eats_nomenclature, pgsql, should_include_pennies_in_price,
):
    expected_products = get_products(pgsql, ASSORTMENT_ID)

    if not should_include_pennies_in_price:
        for item in expected_products:
            list_item = list(item)
            expected_products.remove(item)
            list_item[2] = pennies_utils.proper_round(list_item[2])
            expected_products.add(tuple(list_item))

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
    )

    assert response.status == 200

    assert map_response(response.json()) == expected_products


def map_response(json):
    categories = json['categories']
    products = []
    for category in categories:
        products += category['items']

    return {
        (
            p['is_available'],
            p.get('location') or None,
            p.get('price') or None,
            p.get('old_price') or None,
            p.get('vat') or None,
            p.get('vendor_code') or None,
            p['id'],
            p['description']['general'],
            p['is_catch_weight'],
            p['shipping_type'],
            p['is_choosable'],
            p.get('measure', {}).get('quantum') or 0.0,
            p.get('measure', {}).get('unit') or None,
            p.get('measure', {}).get('value') or None,
            p.get('volume', {}).get('unit') or None,
            p.get('volume', {}).get('value') or None,
            p['name'],
            p.get('description', {}).get('package_info') or None,
            p.get('description', {}).get('expires_in') or None,
            p.get('description', {}).get('storage_requirements') or None,
            p.get('description', {}).get('purpose') or None,
            p.get('description', {}).get('nutritional_value') or None,
            p.get('description', {}).get('composition') or None,
            p['adult'],
            p['sort_order'],
        )
        for p in products
    }


def get_products(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
select
   case
     when pp.available_from < now()
       and (s.value is null or s.value > 0)
       and (pp.force_unavailable_until is null
                or pp.force_unavailable_until < now())
       then true
     else false
   end is_available,
   null as location,
   cast(pp.price as double precision) price,
   case
     when pp.old_price = 0.0
       then null
     else round(cast(pp.old_price as double precision))
   end old_price,
   pp.vat,
   null as vendor_code,
   p.origin_id id,
   p.description,
   p.is_catch_weight,
   st.value shipping_type,
   p.is_choosable,
   p.quantum,
   mu.value measure_unit,
   p.measure_value,
   vu.value volume_unit,
   p.volume_value,
   p.name,
   p.package_info,
   p.expires_in,
   p.storage_requirements,
   p.purpose,
   p.nutritional_value,
   p.composition,
   p.adult,
   cp.sort_order
from eats_nomenclature.categories_products cp
join eats_nomenclature.products p on p.id = cp.product_id
join eats_nomenclature.places_products pp on pp.product_id = p.id
left join eats_nomenclature.shipping_types st on st.id = p.shipping_type_id
left join eats_nomenclature.measure_units mu on mu.id = p.measure_unit_id
left join eats_nomenclature.volume_units vu on vu.id = p.volume_unit_id
left join eats_nomenclature.stocks s on s.place_product_id = pp.id
where pp.price > 0 and cp.assortment_id=%s
order by pp.origin_id""",
        (assortment_id,),
    )
    return set(cursor)
