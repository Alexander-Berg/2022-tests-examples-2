import pytest

from taxi.codegen import clients_base_exceptions

from eats_order_integration.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_order_integration.crontasks.update_integration_engines',
    '-t',
    '0',
]

EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS = {'enabled': True}


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS={
        'enabled': False,
    },
)
async def test_should_not_start_if_disabled(mock_eats_core_order_integration):
    @mock_eats_core_order_integration('/v1/integration-engines')
    async def mock_get_integration_engines():
        return {}

    await run_cron.main(CRON_SETTINGS)

    assert not mock_get_integration_engines.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS=EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS,  # noqa: E501
)
async def test_should_fail_if_nothing_updated(
        mock_eats_core_order_integration,
):
    @mock_eats_core_order_integration('/v1/integration-engines')
    async def mock_get_integration_engines(request):
        return {'items': []}

    with pytest.raises(Exception, match='No integration engines updated'):
        await run_cron.main(CRON_SETTINGS)

    assert mock_get_integration_engines.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS=EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS,  # noqa: E501
)
async def test_should_insert_new(
        cron_context, mock_eats_core_order_integration, pgsql, load_json,
):
    @mock_eats_core_order_integration('/v1/integration-engines')
    async def mock_get_integration_engines(request):
        return load_json('integration_engines_response.json')['insert_new']

    assert _get_count(pgsql, 'integration_engines') == 2

    await run_cron.main(CRON_SETTINGS)

    assert mock_get_integration_engines.times_called == 1
    assert _get_count(pgsql, 'integration_engines') == 3
    await _check_integration_engines_data(
        pgsql, load_json, 'insert_new', cron_context,
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS=EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS,  # noqa: E501
)
async def test_should_update_existing(
        cron_context, mock_eats_core_order_integration, pgsql, load_json,
):
    @mock_eats_core_order_integration('/v1/integration-engines')
    async def mock_get_integration_engines(request):
        return load_json('integration_engines_response.json')[
            'update_existing'
        ]

    assert _get_count(pgsql, 'integration_engines') == 2

    await run_cron.main(CRON_SETTINGS)

    assert mock_get_integration_engines.times_called == 1
    assert _get_count(pgsql, 'integration_engines') == 2
    await _check_integration_engines_data(
        pgsql, load_json, 'update_existing', cron_context,
    )


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS=EATS_ORDER_INTEGRATION_UPDATE_INTEGRATION_ENGINES_SETTINGS,  # noqa: E501
)
async def test_should_raise_exception_and_client_has_retries(
        mock_eats_core_order_integration, load_json, mockserver,
):
    @mock_eats_core_order_integration('/v1/integration-engines')
    async def mock_get_integration_engines(request):
        return mockserver.make_response(status=500)

    with pytest.raises(clients_base_exceptions.ClientException):
        await run_cron.main(CRON_SETTINGS)

    # 2 because of retries in client
    assert mock_get_integration_engines.times_called == 2


def _get_count(pgsql, table_name):
    with pgsql['eats_order_integration'].cursor() as cursor:
        cursor.execute(f'select count(*) from {table_name}')
        count = list(row[0] for row in cursor)[0]
    return count


async def _check_integration_engines_data(
        pgsql, load_json, data_name, cron_context,
):
    expected_data = load_json('integration_engines_db_data.json')[data_name]
    with pgsql['eats_order_integration'].dict_cursor() as cursor:
        cursor.execute('SELECT * FROM integration_engines')
        actual_data = [row for row in cursor]

    for i, expected_elem in enumerate(expected_data):
        actual_elem = actual_data[i]

        assert actual_elem['id'] == expected_elem['id']
        assert actual_elem['name'] == expected_elem['name']
        assert actual_elem['is_hidden'] == expected_elem['is_hidden']
        assert actual_elem['engine_class'] == expected_elem['engine_class']
