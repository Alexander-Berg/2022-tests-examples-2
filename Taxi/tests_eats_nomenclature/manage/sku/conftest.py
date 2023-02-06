import pytest


def _measure_to_str_or_null(sku, field):
    if field not in sku:
        return 'null'
    value = sku[field]['value']
    unit = ''
    if 'unit' in sku[field]:
        unit = ' ' + sku[field]['unit']
    return f'\'{value}{unit}\''


def _value_to_str_or_null(sku, field):
    if field not in sku or sku[field] is None:
        return 'null'
    return f'\'{sku[field]}\''


def _value_or_null(sku, field):
    if field not in sku:
        return 'null'
    return f'{sku[field]}'


@pytest.fixture(name='sql_insert_sku')
def _sql_insert_sku(pg_realdict_cursor):
    def do_smth(sku, sku_uuid):
        weight = _measure_to_str_or_null(sku, 'weight')
        volume = _measure_to_str_or_null(sku, 'volume')
        calories = _measure_to_str_or_null(sku, 'calories')
        expiration_info = _measure_to_str_or_null(sku, 'expiration_info')
        composition = _value_to_str_or_null(sku, 'composition')
        carbohydrates = _value_to_str_or_null(sku, 'carbohydrates')
        proteins = _value_to_str_or_null(sku, 'proteins')
        fats = _value_to_str_or_null(sku, 'fats')
        storage_requirements = _value_to_str_or_null(
            sku, 'storage_requirements',
        )
        package_info = _value_to_str_or_null(sku, 'package_info')
        country = _value_to_str_or_null(sku, 'country')
        is_alcohol = _value_or_null(sku, 'is_alcohol')
        is_fresh = _value_or_null(sku, 'is_fresh')
        is_adult = _value_or_null(sku, 'is_adult')
        fat_content = _value_to_str_or_null(sku, 'fat_content')
        milk_type = _value_to_str_or_null(sku, 'milk_type')
        cultivar = _value_to_str_or_null(sku, 'cultivar')
        flavour = _value_to_str_or_null(sku, 'flavour')
        meat_type = _value_to_str_or_null(sku, 'meat_type')
        carcass_part = _value_to_str_or_null(sku, 'carcass_part')
        egg_category = _value_to_str_or_null(sku, 'egg_category')
        alco_grape_cultivar = _value_to_str_or_null(sku, 'alco_grape_cultivar')
        alco_aroma = _value_to_str_or_null(sku, 'alco_aroma')
        alco_flavour = _value_to_str_or_null(sku, 'alco_flavour')
        alco_pairing = _value_to_str_or_null(sku, 'alco_pairing')

        pg_realdict_cursor.execute(
            f"""
        insert into eats_nomenclature.sku (
            uuid, alternate_name, weight, volume, composition,
            сarbohydrates, proteins, fats, calories,
            storage_requirements, expiration_info, package_type,
            country, is_alcohol, is_fresh, is_adult,
            fat_content, milk_type, cultivar, flavour, meat_type,
            carcass_part, egg_category, alco_grape_cultivar,
            alco_aroma, alco_flavour, alco_pairing
        )
        values (
            '{sku_uuid}', '{sku['name']}', {weight},
            {volume}, {composition}, {carbohydrates},
            {proteins}, {fats}, {calories},
            {storage_requirements}, {expiration_info},
            {package_info}, {country}, {is_alcohol},
            {is_fresh}, {is_adult}, {fat_content}, {milk_type},
            {cultivar}, {flavour}, {meat_type},
            {carcass_part}, {egg_category}, {alco_grape_cultivar},
            {alco_aroma}, {alco_flavour}, {alco_pairing}
        )
        returning id
        """,
        )
        return pg_realdict_cursor.fetchall()[0]['id']

    return do_smth


@pytest.fixture(name='sql_insert_sku_pictures')
def _sql_insert_sku_pictures(pg_realdict_cursor):
    def do_smth(sku_id, sku_images):
        for image in sku_images:
            pg_realdict_cursor.execute(
                f"""
        insert into eats_nomenclature.pictures (
            url
        )
        values (
            '{image['url']}'
        )
        returning id
        """,
            )
            picture_id = pg_realdict_cursor.fetchall()[0]['id']

            retailer_slug = 'null'
            if 'brand_slug' in image:
                pg_realdict_cursor.execute(
                    f"""
        select r.slug retailer_slug from eats_nomenclature.retailers r
            join eats_nomenclature.brands b
            on r.id = b.retailer_id
        where b.slug = '{image['brand_slug']}'
        """,
                )
                row = pg_realdict_cursor.fetchall()[0]
                retailer_slug = f"""'{row['retailer_slug']}'"""

            pg_realdict_cursor.execute(
                f"""
        insert into eats_nomenclature.sku_pictures (
            sku_id, picture_id, retailer_name
        )
        values (
            {sku_id}, {picture_id}, {retailer_slug}
        )
        """,
            )

    return do_smth


@pytest.fixture(name='sql_insert_brands')
def _sql_insert_brands(pg_realdict_cursor):
    def do_smth(num_of_brands=3):
        for brand_id in range(1, num_of_brands + 1):
            pg_realdict_cursor.execute(
                f"""
        insert into eats_nomenclature.retailers (
            id, name, slug
        )
        values (
            {brand_id}, 'name_{brand_id}', 'retailer_slug_{brand_id}'
        )
        """,
            )

            pg_realdict_cursor.execute(
                f"""
        insert into eats_nomenclature.brands (
            id, name, slug, retailer_id
        )
        values (
            {brand_id}, 'name_{brand_id}', 'brand_slug_{brand_id}', {brand_id}
        )
        """,
            )

    return do_smth


def _split_measure(measure):
    value, unit = measure.split()
    return {'value': value, 'unit': unit}


@pytest.fixture(name='sql_select_sku_data')
def _sql_select_sku_data(pg_realdict_cursor):
    def do_smth(sku_id):
        pg_realdict_cursor.execute(
            f"""
        select alternate_name as name, weight, volume, composition,
               сarbohydrates as carbohydrates, proteins, fats, calories,
               storage_requirements, expiration_info, country,
               package_type as package_info, is_alcohol, is_fresh, is_adult,
               fat_content, milk_type, cultivar, flavour, meat_type,
               carcass_part, egg_category, alco_grape_cultivar, alco_aroma,
               alco_flavour, alco_pairing
        from eats_nomenclature.sku
        where id = {sku_id}
        """,
        )
        sku_data = pg_realdict_cursor.fetchall()[0]
        sku_data['weight'] = _split_measure(sku_data['weight'])
        sku_data['volume'] = _split_measure(sku_data['volume'])
        sku_data['calories'] = _split_measure(sku_data['calories'])
        sku_data['expiration_info'] = _split_measure(
            sku_data['expiration_info'],
        )
        sku_data['fat_content'] = (
            str(float(sku_data['fat_content']))
            if sku_data['fat_content']
            else None
        )

        pg_realdict_cursor.execute(
            f"""
        select b.slug as brand_slug, url
from eats_nomenclature.sku_pictures sp
            join eats_nomenclature.pictures p
            on sp.picture_id = p.id
                left join eats_nomenclature.retailers r
                on r.slug = sp.retailer_name
                    left join eats_nomenclature.brands b
                    on r.id = b.retailer_id
        where sku_id = {sku_id}
        """,
        )
        sku_pictures = pg_realdict_cursor.fetchall()
        sku_data['images'] = []
        for sku_picture in sku_pictures:
            image = {'url': sku_picture['url']}
            if 'brand_slug' in sku_picture and sku_picture['brand_slug']:
                image['brand_slug'] = sku_picture['brand_slug']
            sku_data['images'].append(image)
        return sku_data

    return do_smth


@pytest.fixture(name='generate_sku_data')
def _generate_sku_data():
    def do_smth(
            index,
            weight_unit,
            volume_unit,
            calories_unit,
            expiration_info_unit,
            is_alcohol,
            is_fresh,
            is_adult,
            images,
            generate_attributes=False,
    ):
        return {
            'name': f'Sku name {index}',
            'weight': {'value': str(100 * index), 'unit': weight_unit},
            'volume': {'value': str(100 * index), 'unit': volume_unit},
            'composition': f'Composition {index}',
            'carbohydrates': str(1 * index),
            'proteins': str(2 * index),
            'fats': str(3 * index),
            'calories': {'value': str(100 * index), 'unit': calories_unit},
            'storage_requirements': f'Storage requirements {index}',
            'expiration_info': {
                'value': str(10 * index),
                'unit': expiration_info_unit,
            },
            'package_info': f'Package info {index}',
            'country': f'Country {index}',
            'is_alcohol': is_alcohol,
            'is_fresh': is_fresh,
            'is_adult': is_adult,
            'images': images,
            'fat_content': '1.1' if generate_attributes else None,
            'milk_type': f'Milk type {index}' if generate_attributes else None,
            'cultivar': f'Cultivar {index}' if generate_attributes else None,
            'flavour': f'Flavour {index}' if generate_attributes else None,
            'meat_type': f'Meat type {index}' if generate_attributes else None,
            'carcass_part': (
                f'Carcass part {index}' if generate_attributes else None
            ),
            'egg_category': (
                f'Egg category {index}' if generate_attributes else None
            ),
            'alco_grape_cultivar': (
                f'Alco grape cultivar {index}' if generate_attributes else None
            ),
            'alco_aroma': (
                f'Alco aroma {index}' if generate_attributes else None
            ),
            'alco_flavour': (
                f'Alco flavour {index}' if generate_attributes else None
            ),
            'alco_pairing': (
                f'Alco pairing {index}' if generate_attributes else None
            ),
        }

    return do_smth
