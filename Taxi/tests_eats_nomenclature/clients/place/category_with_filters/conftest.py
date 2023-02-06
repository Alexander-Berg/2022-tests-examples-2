import pytest


@pytest.fixture(name='sql_set_sku_product_attribute')
def _sql_set_sku_product_attribute(pgsql):
    def do_smth(field_name, ids_with_attributes):
        cursor = pgsql['eats_nomenclature'].cursor()
        for sku_id, attribute in ids_with_attributes:
            if field_name == 'volume' and attribute[-1] != 'л':
                attribute += ' мл'
            cursor.execute(
                f"""update eats_nomenclature.sku
                    set
                        {field_name} = '{attribute}'
                    where id = {sku_id}
                """,
            )

    return do_smth


@pytest.fixture(name='sql_set_sku_brand')
def _sql_set_sku_brand(pgsql):
    def do_smth(sku_ids_with_brand_ids):
        cursor = pgsql['eats_nomenclature'].cursor()
        for sku_id, brand_id in sku_ids_with_brand_ids:
            cursor.execute(
                f"""insert into eats_nomenclature.sku_attributes(sku_id, product_brand_id)
                    values ({sku_id}, {brand_id})
                """,
            )

    return do_smth
