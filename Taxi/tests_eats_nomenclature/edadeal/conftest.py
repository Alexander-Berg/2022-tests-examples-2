import pytest


@pytest.fixture(name='get_edadeal_export_task')
def _get_edadeal_export_task(get_cursor):
    def do_get_edadeal_export_task(export_task_id):
        cursor = get_cursor()
        cursor.execute(
            f"""
            select id, brand_id, s3_export_path,
            export_retailer_name, exported_at,
            processed, updated_at
            from eats_nomenclature.edadeal_export_tasks
            where id = {export_task_id}
            """,
        )
        raw_result = list(cursor)
        if not raw_result:
            return {}
        result = raw_result[0]
        return {
            'id': result[0],
            'brand_id': result[1],
            's3_export_path': result[2],
            'export_retailer_name': result[3],
            'exported_at': result[4],
            'processed': result[5],
            'updated_at': result[6],
        }

    return do_get_edadeal_export_task


@pytest.fixture(name='delete_edadeal_export_task')
def _delete_edadeal_export_task(get_cursor):
    def do_delete_edadeal_export_task(export_task_id):
        cursor = get_cursor()
        cursor.execute(
            f"""
            delete from eats_nomenclature.edadeal_export_tasks
            where id = {export_task_id}
            """,
        )

    return do_delete_edadeal_export_task


@pytest.fixture(name='get_edadeal_import_task')
def _get_edadeal_import_task(get_cursor):
    def do_get_edadeal_import_task(task_type, export_task_id):
        if task_type == 'tag':
            table_name = 'edadeal_tag_import_tasks'
        else:
            table_name = 'edadeal_sku_import_tasks'
        cursor = get_cursor()
        cursor.execute(
            f"""
            select id, edadeal_export_task_id, yt_path,
            status, details, updated_at
            from eats_nomenclature.{table_name}
            where edadeal_export_task_id = {export_task_id}
            """,
        )
        raw_result = list(cursor)
        if not raw_result:
            return {}
        result = raw_result[0]
        return {
            'id': result[0],
            'edadeal_export_task_id': result[1],
            'yt_path': result[2],
            'status': result[3],
            'details': result[4],
            'updated_at': result[5],
        }

    return do_get_edadeal_import_task


@pytest.fixture(name='get_import_task_status_history')
def _get_import_task_status_history(get_cursor):
    def do_get_history(task_type, import_task_id):
        if task_type == 'tag':
            table_name = 'edadeal_tag_import_task_status_history'
        else:
            table_name = 'edadeal_sku_import_task_status_history'
        cursor = get_cursor()
        cursor.execute(
            f"""
            select import_task_id, status, details, set_at
            from eats_nomenclature.{table_name}
            where import_task_id = {import_task_id}
            """,
        )
        return [
            {
                'import_task_id': result[0],
                'status': result[1],
                'details': result[2],
                'set_at': result[3],
            }
            for result in list(cursor)
        ]

    return do_get_history


@pytest.fixture(name='create_edadeal_import_task')
def _create_edadeal_import_task(get_cursor):
    def do_create_edadeal_import_task(task_type, export_task_id, yt_path):
        if task_type == 'tag':
            table_name = 'edadeal_tag_import_tasks'
        else:
            table_name = 'edadeal_sku_import_tasks'
        cursor = get_cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.{table_name}
            (edadeal_export_task_id, yt_path, details)
            values ({export_task_id}, '{yt_path}', '')
            returning id
            """,
        )
        return cursor.fetchone()[0]

    return do_create_edadeal_import_task


@pytest.fixture(name='delete_edadeal_import_task')
def _delete_edadeal_import_task(get_cursor):
    def do_delete_edadeal_import_task(task_type, export_task_id):
        if task_type == 'tag':
            table_name = 'edadeal_tag_import_tasks'
        else:
            table_name = 'edadeal_sku_import_tasks'
        cursor = get_cursor()
        cursor.execute(
            f"""
            delete from eats_nomenclature.{table_name}
            where edadeal_export_task_id = {export_task_id}
            """,
        )

    return do_delete_edadeal_import_task


@pytest.fixture(name='get_product_brand')
def _get_product_brand(get_cursor):
    def do_get_product_brand(product_brand_id):
        cursor = get_cursor()
        cursor.execute(
            f"""
            select id, value_uuid, value
            from eats_nomenclature.product_brands
            where id = {product_brand_id}
            """,
        )
        raw_result = list(cursor)
        if not raw_result:
            return {}
        result = raw_result[0]
        return {'id': result[0], 'value_uuid': result[1], 'value': result[2]}

    return do_get_product_brand


@pytest.fixture(name='create_product_brand')
def _create_product_brand(get_cursor):
    def do_create_product_brand(attr_value_uuid, attr_value):
        cursor = get_cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.product_brands
            (value_uuid, value)
            values (
                '{attr_value_uuid}',
                '{attr_value}'
            )
            returning id
            """,
        )
        return cursor.fetchone()[0]

    return do_create_product_brand


@pytest.fixture(name='get_product_type')
def _get_product_type(get_cursor):
    def do_get_product_type(product_type_id):
        cursor = get_cursor()
        cursor.execute(
            f"""
            select id, value_uuid, value
            from eats_nomenclature.product_types
            where id = {product_type_id}
            """,
        )
        raw_result = list(cursor)
        if not raw_result:
            return {}
        result = raw_result[0]
        return {'id': result[0], 'value_uuid': result[1], 'value': result[2]}

    return do_get_product_type


@pytest.fixture(name='create_product_type')
def _create_product_type(get_cursor):
    def do_create_product_type(attr_value_uuid, attr_value):
        cursor = get_cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.product_types
            (value_uuid, value)
            values (
                '{attr_value_uuid}',
                '{attr_value}'
            ) on conflict (value) do nothing
            returning id
            """,
        )
        insert_result = cursor.fetchone()
        if insert_result:
            return insert_result[0]
        return None

    return do_create_product_type


@pytest.fixture(name='get_product_processing_type')
def _get_product_processing_type(get_cursor):
    def do_get_product_processing_type(product_processing_type_id):
        cursor = get_cursor()
        cursor.execute(
            f"""
            select id, value_uuid, value
            from eats_nomenclature.product_processing_types
            where id = {product_processing_type_id}
            """,
        )
        raw_result = list(cursor)
        if not raw_result:
            return {}
        result = raw_result[0]
        return {'id': result[0], 'value_uuid': result[1], 'value': result[2]}

    return do_get_product_processing_type


@pytest.fixture(name='create_product_processing_type')
def _create_product_processing_type(get_cursor):
    def do_create(attr_value_uuid, attr_value):
        cursor = get_cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.product_processing_types
            (value_uuid, value)
            values (
                '{attr_value_uuid}',
                '{attr_value}'
            )
            returning id
            """,
        )
        return cursor.fetchone()[0]

    return do_create


@pytest.fixture(name='get_product_attributes')
def _get_product_attributes(pg_realdict_cursor):
    def do_get_product_attributes(product_id):
        pg_realdict_cursor.execute(
            f"""
            select
                product_id,
                product_brand_id,
                product_type_id,
                product_processing_type_id
            from eats_nomenclature.product_attributes
            where product_id = {product_id}
            """,
        )
        return pg_realdict_cursor.fetchone()

    return do_get_product_attributes


@pytest.fixture(name='create_product_attributes')
def _create_product_attributes(get_cursor):
    def do_create_product_attributes(
            product_id,
            product_brand_id=None,
            product_type_id=None,
            product_processing_type_id=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            f"""
            insert into eats_nomenclature.product_attributes
            (product_id,
             product_brand_id,
             product_type_id,
             product_processing_type_id)
            values (%s, %s, %s, %s)
            """,
            (
                product_id,
                product_brand_id,
                product_type_id,
                product_processing_type_id,
            ),
        )

    return do_create_product_attributes


@pytest.fixture(name='edadeal_tags_enqueue')
def _edadeal_tags_enqueue(stq_runner):
    async def do_edadeal_tags_enqueue(task_id=1, expect_fail=False):
        await stq_runner.eats_nomenclature_edadeal_tags_processing.call(
            task_id=f'tags_processing_{task_id}',
            args=[],
            kwargs={'import_task_id': task_id},
            expect_fail=expect_fail,
        )

    return do_edadeal_tags_enqueue
