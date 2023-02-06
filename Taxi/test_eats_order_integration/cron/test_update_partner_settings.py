import pytest

from eats_order_integration.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_order_integration.crontasks.update_partner_settings',
    '-t',
    '0',
]


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'test1'}],
        value={'engine_name': 'test1', 'engine_class_name': 'YandexEdaEngine'},
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': False,
    },
)
async def test_should_not_start_if_disabled(mock_eats_core_retail):
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve():
        return {}

    await run_cron.main(CRON_SETTINGS)

    assert not mock_brands_retrieve.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
    },
)
async def test_should_fail_if_nothing_updated(mock_eats_core_retail):
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve(request):
        return {'brands': []}

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve/page-count')
    async def mock_page_count(request):  # pylint:disable=unused-variable
        return {'page_count': 0}

    with pytest.raises(Exception, match='No credentials updated'):
        await run_cron.main(CRON_SETTINGS)

    assert mock_brands_retrieve.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
        'place_groups_rate_limit': 10,
        'integration_engines': [1],
    },
)
async def test_should_insert_new(
        cron_context, mock_eats_core_retail, pgsql, load_json,
):
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve(request):
        return load_json('brands_response.json')

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve/page-count')
    async def mock_page_count(request):  # pylint:disable=unused-variable
        return {'page_count': 1}

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return load_json('place_groups_response.json')['new']

    assert _get_count(pgsql, 'partner_engine_settings') == 1

    await run_cron.main(CRON_SETTINGS)

    assert mock_brands_retrieve.times_called == 1
    assert mock_place_groups_retrieve.times_called == 1
    assert _get_count(pgsql, 'partner_engine_settings') == 2
    await _check_partners_credentials_data(
        pgsql, load_json, 'insert_new', cron_context,
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
        'place_groups_rate_limit': 10,
        'integration_engines': [1],
    },
)
async def test_should_update_existing(
        cron_context, mock_eats_core_retail, pgsql, load_json,
):
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve(request):
        return load_json('brands_response.json')

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve/page-count')
    async def mock_page_count(request):  # pylint:disable=unused-variable
        return {'page_count': 1}

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return load_json('place_groups_response.json')['existing']

    assert _get_count(pgsql, 'partner_engine_settings') == 1

    await run_cron.main(CRON_SETTINGS)

    assert mock_brands_retrieve.times_called == 1
    assert mock_place_groups_retrieve.times_called == 1
    assert _get_count(pgsql, 'partner_engine_settings') == 1
    await _check_partners_credentials_data(
        pgsql, load_json, 'update_existing', cron_context,
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
        'place_groups_rate_limit': 10,
        'integration_engines': [1],
    },
)
async def test_should_raise_exception_and_client_has_retries(
        mock_eats_core_retail, load_json, mockserver,
):
    # pylint: disable=unused-variable
    @mock_eats_core_retail('/v1/brands/retrieve')
    async def mock_brands_retrieve(request):
        return load_json('brands_response.json')

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve/page-count')
    async def mock_page_count(request):  # pylint:disable=unused-variable
        return mockserver.make_response(json={'page_count': 1})

    @mock_eats_core_retail('/v1/place-groups/order-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return mockserver.make_response(status=500)

    with pytest.raises(
            Exception, match='Error occurred when update partners credentials',
    ):
        await run_cron.main(CRON_SETTINGS)

    assert mock_place_groups_retrieve.times_called == 2


def _get_count(pgsql, table_name):
    with pgsql['eats_order_integration'].cursor() as cursor:
        cursor.execute(f'select count(*) from {table_name}')
        count = list(row[0] for row in cursor)[0]
    return count


async def _check_partners_credentials_data(
        pgsql, load_json, data_name, cron_context,
):
    expected_data = load_json('retail_info_data.json')[data_name]
    with pgsql['eats_order_integration'].dict_cursor() as cursor:
        cursor.execute('SELECT * FROM partner_engine_settings')
        actual_data = [row for row in cursor]

    for i, expected_elem in enumerate(expected_data):
        encrypted_elem = actual_data[i]

        encrypted_credentials = encrypted_elem['credentials']
        actual_elem = (
            await cron_context.retail_encryption.decrypt_dynamic_object(
                encrypted_credentials, ['client_id', 'client_secret'],
            )
        )

        assert (
            encrypted_elem['place_group_id'] == expected_elem['place_group_id']
        )
        assert actual_elem['client_id'] == expected_elem['client_id']
        assert actual_elem['client_secret'] == expected_elem['client_secret']
        assert actual_elem['vendor_host'] == expected_elem['vendor_host']
        assert actual_elem['scope'] == expected_elem['scope']
