# pylint: disable=too-many-lines
import datetime as dt

import pytest

TEST_EXPORT_TASK_ID = 1
TEST_TAG_IMPORT_TASK_ID = 1
TEST_YT_PATH = '//edadeal_yt/proccessed/bystronom/2019-12-06'
TEST_PRODUCT_ID = 1
TEST_PRODUCT_ID2 = 2
TEST_PRODUCT_BRAND = {
    'id': 1,
    'value': 'Gourmet',
    'value_uuid': 'd74dd8e6-9515-564b-b184-8cc3ab4bf0af',
}
TEST_PRODUCT_BRAND2 = {
    'id': 2,
    'value': 'Fleur Alpine 2',
    'value_uuid': '40a7405a-84f7-5468-99c5-94d91a2e0102',
}
TEST_PRODUCT_TYPE = {
    'id': 1,
    'value': 'Корм для кошек',
    'value_uuid': '7ee63ec3-7b32-583f-bfc1-1f37bba84a72',
}
TEST_PRODUCT_TYPE2 = {
    'id': 2,
    'value': 'Печенье детское 2',
    'value_uuid': '3df0d4be-644f-5a23-b912-5e6f29fe5322',
}
TEST_PRODUCT_PROCESSING_TYPE = {
    'id': 1,
    'value': 'охлаждённый',
    'value_uuid': 'f8e0fec3-5005-430e-a52c-2b65c41ad862',
}
TEST_PRODUCT_PROCESSING_TYPE2 = {
    'id': 2,
    'value': 'замороженный',
    'value_uuid': '0710715e-2c7b-4206-a2b5-b8f3a075aad3',
}


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_add_product_brand(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_brand,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_brand = get_product_brand(
        product_brand_id=TEST_PRODUCT_BRAND['id'],
    )
    assert not product_brand

    await edadeal_tags_enqueue()

    product_brand = get_product_brand(
        product_brand_id=TEST_PRODUCT_BRAND['id'],
    )
    assert product_brand['value'] == TEST_PRODUCT_BRAND['value']
    assert product_brand['value_uuid'] == TEST_PRODUCT_BRAND['value_uuid']

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
@pytest.mark.parametrize(
    'existing_value',
    [
        pytest.param(TEST_PRODUCT_BRAND['value'], id='same value'),
        pytest.param('Test old value', id='another value'),
    ],
)
async def test_add_existing_product_brand(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        create_product_brand,
        get_product_brand,
        existing_value,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_brand_id = create_product_brand(
        attr_value_uuid=TEST_PRODUCT_BRAND['value_uuid'],
        attr_value=existing_value,
    )
    product_brand_id2 = create_product_brand(
        attr_value_uuid=TEST_PRODUCT_BRAND2['value_uuid'],
        attr_value=existing_value,
    )

    await edadeal_tags_enqueue()

    product_brand = get_product_brand(product_brand_id=product_brand_id)
    assert product_brand['value'] == TEST_PRODUCT_BRAND['value']
    assert product_brand['value_uuid'] == TEST_PRODUCT_BRAND['value_uuid']

    product_brand2 = get_product_brand(product_brand_id=product_brand_id2)
    assert product_brand2['value'] == TEST_PRODUCT_BRAND2['value']
    assert product_brand2['value_uuid'] == TEST_PRODUCT_BRAND2['value_uuid']

    next_product_brand_id = product_brand_id2 + 1
    product_brand = get_product_brand(product_brand_id=next_product_brand_id)
    assert not product_brand

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_add_product_type(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_type = get_product_type(product_type_id=TEST_PRODUCT_TYPE['id'])
    assert not product_type

    await edadeal_tags_enqueue()

    product_type = get_product_type(product_type_id=TEST_PRODUCT_TYPE['id'])
    assert product_type['value'] == TEST_PRODUCT_TYPE['value']
    assert product_type['value_uuid'] == TEST_PRODUCT_TYPE['value_uuid']

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
@pytest.mark.parametrize(
    'existing_value_uuid',
    [
        pytest.param(TEST_PRODUCT_TYPE['value_uuid'], id='same value_uuid'),
        pytest.param(
            '11111111-1111-1111-1111-11111111', id='another value_uuid',
        ),
    ],
)
async def test_add_existing_product_type(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        create_product_type,
        get_product_type,
        existing_value_uuid,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_type_id = create_product_type(
        attr_value_uuid=existing_value_uuid,
        attr_value=TEST_PRODUCT_TYPE['value'],
    )
    product_type_id2 = create_product_type(
        attr_value_uuid=TEST_PRODUCT_TYPE2['value_uuid'],
        attr_value=TEST_PRODUCT_TYPE['value'],
    )
    assert not product_type_id2

    await edadeal_tags_enqueue()

    product_type = get_product_type(product_type_id=product_type_id)
    assert product_type['value'] == TEST_PRODUCT_TYPE['value']
    assert product_type['value_uuid'] == TEST_PRODUCT_TYPE['value_uuid']

    next_product_type_id = product_type_id + 1
    product_type = get_product_type(product_type_id=next_product_type_id)
    assert not product_type

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_add_product_processing_type(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_processing_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_processing_type = get_product_processing_type(
        product_processing_type_id=TEST_PRODUCT_PROCESSING_TYPE['id'],
    )
    assert not product_processing_type

    await edadeal_tags_enqueue()

    product_processing_type = get_product_processing_type(
        product_processing_type_id=TEST_PRODUCT_PROCESSING_TYPE['id'],
    )
    assert (
        product_processing_type['value']
        == TEST_PRODUCT_PROCESSING_TYPE['value']
    )
    assert (
        product_processing_type['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE['value_uuid']
    )

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
@pytest.mark.parametrize(
    'existing_value',
    [
        pytest.param(TEST_PRODUCT_PROCESSING_TYPE['value'], id='same value'),
        pytest.param('Test old value', id='another value'),
    ],
)
async def test_add_existing_product_processing_type(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        create_product_processing_type,
        get_product_processing_type,
        existing_value,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_processing_type_id = create_product_processing_type(
        attr_value_uuid=TEST_PRODUCT_PROCESSING_TYPE['value_uuid'],
        attr_value=existing_value,
    )
    product_processing_type_id2 = create_product_processing_type(
        attr_value_uuid=TEST_PRODUCT_PROCESSING_TYPE2['value_uuid'],
        attr_value=existing_value,
    )

    await edadeal_tags_enqueue()

    product_processing_type = get_product_processing_type(
        product_processing_type_id=product_processing_type_id,
    )
    assert (
        product_processing_type['value']
        == TEST_PRODUCT_PROCESSING_TYPE['value']
    )
    assert (
        product_processing_type['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE['value_uuid']
    )

    product_processing_type2 = get_product_processing_type(
        product_processing_type_id=product_processing_type_id2,
    )
    assert (
        product_processing_type2['value']
        == TEST_PRODUCT_PROCESSING_TYPE2['value']
    )
    assert (
        product_processing_type2['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE2['value_uuid']
    )

    next_product_processing_type_id = product_processing_type_id2 + 1
    product_processing_type = get_product_processing_type(
        product_processing_type_id=next_product_processing_type_id,
    )
    assert not product_processing_type

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_add_product_attributes(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_brand,
        get_product_type,
        get_product_processing_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert product_attributes['product_brand_id']
    assert product_attributes['product_type_id']
    assert product_attributes['product_processing_type_id']

    product_brand = get_product_brand(
        product_brand_id=product_attributes['product_brand_id'],
    )
    assert product_brand['value'] == TEST_PRODUCT_BRAND['value']
    assert product_brand['value_uuid'] == TEST_PRODUCT_BRAND['value_uuid']

    product_type = get_product_type(
        product_type_id=product_attributes['product_type_id'],
    )
    assert product_type['value'] == TEST_PRODUCT_TYPE['value']
    assert product_type['value_uuid'] == TEST_PRODUCT_TYPE['value_uuid']

    product_processing_type = get_product_processing_type(
        product_processing_type_id=product_attributes[
            'product_processing_type_id'
        ],
    )
    assert (
        product_processing_type['value']
        == TEST_PRODUCT_PROCESSING_TYPE['value']
    )
    assert (
        product_processing_type['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE['value_uuid']
    )

    second_product_attributes = get_product_attributes(
        product_id=TEST_PRODUCT_ID2,
    )
    assert not second_product_attributes

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
@pytest.mark.parametrize(
    'is_existing_brand, is_existing_name, is_existing_processing_type',
    [
        pytest.param(False, False, False, id='no_existing'),
        pytest.param(False, False, True, id='existing_processing_type'),
        pytest.param(False, True, False, id='existing_name'),
        pytest.param(True, False, False, id='existing_brand'),
        pytest.param(True, True, True, id='existing_all'),
    ],
)
async def test_add_existing_product_attributes(
        yt_apply,
        taxi_eats_nomenclature,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        create_product_brand,
        create_product_type,
        create_product_processing_type,
        create_product_attributes,
        get_product_attributes,
        get_product_brand,
        get_product_type,
        get_product_processing_type,
        # parametrize params
        is_existing_brand,
        is_existing_name,
        is_existing_processing_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_brand_id = None
    product_type_id = None
    product_processing_type_id = None
    if is_existing_brand:
        product_brand_id = create_product_brand(
            attr_value_uuid=TEST_PRODUCT_BRAND['value_uuid'],
            attr_value='Some old brand',
        )
    if is_existing_name:
        product_type_id = create_product_type(
            attr_value_uuid='11111111-1111-1111-11111111',
            attr_value=TEST_PRODUCT_TYPE['value'],
        )
    if is_existing_processing_type:
        product_processing_type_id = create_product_processing_type(
            attr_value_uuid=TEST_PRODUCT_PROCESSING_TYPE['value_uuid'],
            attr_value='Some old processing type',
        )

    create_product_attributes(
        product_id=TEST_PRODUCT_ID,
        product_brand_id=product_brand_id,
        product_type_id=product_type_id,
        product_processing_type_id=product_processing_type_id,
    )

    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert product_attributes['product_brand_id'] == TEST_PRODUCT_BRAND['id']
    assert product_attributes['product_type_id'] == TEST_PRODUCT_TYPE['id']
    assert (
        product_attributes['product_processing_type_id']
        == TEST_PRODUCT_PROCESSING_TYPE['id']
    )

    if is_existing_brand:
        assert product_attributes['product_brand_id'] == product_brand_id

    if is_existing_name:
        assert product_attributes['product_type_id'] == product_type_id

    if is_existing_processing_type:
        assert (
            product_attributes['product_processing_type_id']
            == product_processing_type_id
        )

    product_brand = get_product_brand(
        product_brand_id=product_attributes['product_brand_id'],
    )
    assert product_brand['value'] == TEST_PRODUCT_BRAND['value']
    assert product_brand['value_uuid'] == TEST_PRODUCT_BRAND['value_uuid']

    product_type = get_product_type(
        product_type_id=product_attributes['product_type_id'],
    )
    assert product_type['value'] == TEST_PRODUCT_TYPE['value']
    assert product_type['value_uuid'] == TEST_PRODUCT_TYPE['value_uuid']

    product_processing_type = get_product_processing_type(
        product_processing_type_id=product_attributes[
            'product_processing_type_id'
        ],
    )
    assert (
        product_processing_type['value']
        == TEST_PRODUCT_PROCESSING_TYPE['value']
    )
    assert (
        product_processing_type['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE['value_uuid']
    )

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data_only_brand.yaml'],
)
async def test_add_only_brand(
        taxi_eats_nomenclature,
        yt_apply,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_brand,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert product_attributes['product_brand_id']
    assert not product_attributes['product_type_id']

    product_brand = get_product_brand(
        product_brand_id=product_attributes['product_brand_id'],
    )
    assert product_brand['value'] == TEST_PRODUCT_BRAND['value']
    assert product_brand['value_uuid'] == TEST_PRODUCT_BRAND['value_uuid']

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data_only_name.yaml'],
)
async def test_add_only_name(
        taxi_eats_nomenclature,
        yt_apply,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes['product_brand_id']
    assert product_attributes['product_type_id']

    product_type = get_product_type(
        product_type_id=product_attributes['product_type_id'],
    )
    assert product_type['value'] == TEST_PRODUCT_TYPE['value']
    assert product_type['value_uuid'] == TEST_PRODUCT_TYPE['value_uuid']

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data_only_processing_type.yaml'],
)
async def test_add_only_processing_type(
        taxi_eats_nomenclature,
        yt_apply,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_processing_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert product_attributes['product_processing_type_id']
    assert not product_attributes['product_type_id']

    product_processing_type = get_product_processing_type(
        product_processing_type_id=product_attributes[
            'product_processing_type_id'
        ],
    )
    assert (
        product_processing_type['value']
        == TEST_PRODUCT_PROCESSING_TYPE['value']
    )
    assert (
        product_processing_type['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE['value_uuid']
    )

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data_matched.yaml'],
)
async def test_not_adding_matched(
        taxi_eats_nomenclature,
        yt_apply,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_brand,
        get_product_type,
        get_product_processing_type,
):
    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'new'

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    product_brand = get_product_brand(
        product_brand_id=TEST_PRODUCT_BRAND['id'],
    )
    assert not product_brand

    product_type = get_product_type(product_type_id=TEST_PRODUCT_TYPE['id'])
    assert not product_type

    product_processing_type = get_product_processing_type(
        product_processing_type_id=TEST_PRODUCT_PROCESSING_TYPE['id'],
    )
    assert not product_processing_type

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_data.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
@pytest.mark.parametrize(
    'no_import_task, no_export_task',
    [
        pytest.param(True, False, id='no import task'),
        pytest.param(True, True, id='no both'),
    ],
)
async def test_no_tasks(
        taxi_eats_nomenclature,
        yt_apply,
        edadeal_tags_enqueue,
        get_edadeal_export_task,
        get_edadeal_import_task,
        get_import_task_status_history,
        delete_edadeal_export_task,
        delete_edadeal_import_task,
        get_product_attributes,
        get_product_brand,
        get_product_type,
        get_product_processing_type,
        no_import_task,
        no_export_task,
):
    if no_import_task:
        delete_edadeal_import_task(
            task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
        )
        tag_import_task = get_edadeal_import_task(
            task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
        )
        assert not tag_import_task

    if no_export_task:
        delete_edadeal_export_task(export_task_id=TEST_EXPORT_TASK_ID)
        export_task = get_edadeal_export_task(
            export_task_id=TEST_EXPORT_TASK_ID,
        )
        assert not export_task

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue(expect_fail=True)

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    product_brand = get_product_brand(
        product_brand_id=TEST_PRODUCT_BRAND['id'],
    )
    assert not product_brand

    product_type = get_product_type(product_type_id=TEST_PRODUCT_TYPE['id'])
    assert not product_type

    product_processing_type = get_product_processing_type(
        product_processing_type_id=TEST_PRODUCT_PROCESSING_TYPE['id'],
    )
    assert not product_processing_type

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=TEST_TAG_IMPORT_TASK_ID,
    )
    assert not task_statuses


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_no_yt_table.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_no_table_in_yt(
        taxi_eats_nomenclature,
        yt_apply,
        edadeal_tags_enqueue,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_brand,
        get_product_type,
        get_product_processing_type,
):
    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    await edadeal_tags_enqueue(expect_fail=True)

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    product_brand = get_product_brand(
        product_brand_id=TEST_PRODUCT_BRAND['id'],
    )
    assert not product_brand

    product_type = get_product_type(product_type_id=TEST_PRODUCT_TYPE['id'])
    assert not product_type

    product_processing_type = get_product_processing_type(
        product_processing_type_id=TEST_PRODUCT_PROCESSING_TYPE['id'],
    )
    assert not product_processing_type

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'error'

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=TEST_TAG_IMPORT_TASK_ID,
    )
    assert len(task_statuses) == 2


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_notify.sql'],
)
@pytest.mark.yt(
    schemas=['yt_export_schema.yaml'],
    static_table_data=['yt_export_data.yaml'],
)
async def test_with_notify(
        taxi_eats_nomenclature,
        testpoint,
        edadeal_tags_enqueue,
        stq,
        yt_apply,
        get_edadeal_export_task,
        get_edadeal_import_task,
        get_import_task_status_history,
        get_product_attributes,
        get_product_brand,
        get_product_type,
        get_product_processing_type,
):
    export_task = get_edadeal_export_task(export_task_id=TEST_EXPORT_TASK_ID)

    request = {
        'brand_id': export_task['brand_id'],
        'retailer_id': f'eda_{export_task["export_retailer_name"]}',
        'timestamp': f'{dt.datetime.utcnow().isoformat("T")}Z',
        's3_path': export_task['s3_export_path'],
        'yt_path': TEST_YT_PATH,
    }
    response = await taxi_eats_nomenclature.post(
        '/v1/edadeal/products/notify_new_data', json=request,
    )
    assert response.status == 204

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['yt_path'] == TEST_YT_PATH
    assert tag_import_task['status'] == 'new'

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert not product_attributes

    # start stq queue
    await edadeal_tags_enqueue()

    product_attributes = get_product_attributes(product_id=TEST_PRODUCT_ID)
    assert product_attributes['product_brand_id']
    assert product_attributes['product_type_id']
    assert product_attributes['product_processing_type_id']

    product_brand = get_product_brand(
        product_brand_id=product_attributes['product_brand_id'],
    )
    assert product_brand['value'] == TEST_PRODUCT_BRAND['value']
    assert product_brand['value_uuid'] == TEST_PRODUCT_BRAND['value_uuid']

    product_type = get_product_type(
        product_type_id=product_attributes['product_type_id'],
    )
    assert product_type['value'] == TEST_PRODUCT_TYPE['value']
    assert product_type['value_uuid'] == TEST_PRODUCT_TYPE['value_uuid']

    product_processing_type = get_product_processing_type(
        product_processing_type_id=product_attributes[
            'product_processing_type_id'
        ],
    )
    assert (
        product_processing_type['value']
        == TEST_PRODUCT_PROCESSING_TYPE['value']
    )
    assert (
        product_processing_type['value_uuid']
        == TEST_PRODUCT_PROCESSING_TYPE['value_uuid']
    )

    second_product_attributes = get_product_attributes(
        product_id=TEST_PRODUCT_ID2,
    )
    assert not second_product_attributes

    task_statuses = get_import_task_status_history(
        task_type='tag', import_task_id=tag_import_task['id'],
    )
    assert len(task_statuses) == 2

    tag_import_task = get_edadeal_import_task(
        task_type='tag', export_task_id=TEST_EXPORT_TASK_ID,
    )
    assert tag_import_task['status'] == 'done'
