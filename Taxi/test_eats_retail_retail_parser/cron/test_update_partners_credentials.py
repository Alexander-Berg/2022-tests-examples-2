import pytest

from eats_retail_encryption.internal import entities

from eats_retail_retail_parser.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_retail_retail_parser.crontasks.update_partners_credentials',
    '-t',
    '0',
]


async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mock_eats_core_retail,
):
    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve/page-count')
    async def mock_page_count_retrieve():
        return {}

    await run_cron.main(CRON_SETTINGS)

    assert not mock_page_count_retrieve.has_calls


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
        'place_groups_rate_limit': 10,
        'parser_names': ['retail_menu'],
    },
)
async def test_should_insert_new_retail_info(
        cron_context, cron_runner, mock_eats_core_retail, pgsql, load_json,
):
    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve/page-count')
    async def mock_page_count_retrieve(request):
        return load_json('pages_response.json')

    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return load_json('place_groups_response.json')['new']

    assert _get_count(pgsql, 'retail_info') == 1

    await run_cron.main(CRON_SETTINGS)

    assert mock_page_count_retrieve.times_called == 1
    assert mock_place_groups_retrieve.times_called == 2
    assert _get_count(pgsql, 'retail_info') == 2
    await _check_retail_info_data(pgsql, load_json, 'insert_new', cron_context)


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
        'place_groups_rate_limit': 10,
        'parser_names': ['retail_menu'],
    },
)
async def test_should_update_existing_retail_info(
        cron_context, cron_runner, mock_eats_core_retail, pgsql, load_json,
):
    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve/page-count')
    async def mock_page_count_retrieve(request):
        return load_json('pages_response.json')

    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return load_json('place_groups_response.json')['existing']

    assert _get_count(pgsql, 'retail_info') == 1

    await run_cron.main(CRON_SETTINGS)

    assert mock_page_count_retrieve.times_called == 1
    assert mock_place_groups_retrieve.times_called == 2
    assert _get_count(pgsql, 'retail_info') == 1
    await _check_retail_info_data(
        pgsql, load_json, 'update_existing', cron_context,
    )


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_UPDATE_PARTNERS_CREDENTIALS_SETTINGS={
        'enabled': True,
        'place_groups_rate_limit': 10,
        'parser_names': ['retail_menu'],
    },
)
async def test_should_raise_exception(
        cron_context,
        cron_runner,
        mock_eats_core_retail,
        load_json,
        mockserver,
):
    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve/page-count')
    async def mock_page_count_retrieve(request):
        return load_json('pages_response.json')

    @mock_eats_core_retail('/v1/place-groups/parser-info/retrieve')
    async def mock_place_groups_retrieve(request):
        return mockserver.make_response(status=500)

    with pytest.raises(Exception, match='Fetch data fail 400'):
        await run_cron.main(CRON_SETTINGS)

    assert mock_place_groups_retrieve.times_called == 4
    assert mock_page_count_retrieve.times_called == 1


def _get_count(pgsql, table_name):
    with pgsql['eats_retail_retail_parser'].cursor() as cursor:
        cursor.execute(f'select count(*) from {table_name}')
        count = list(row[0] for row in cursor)[0]
    return count


async def _check_retail_info_data(pgsql, load_json, data_name, cron_context):
    expected_data = load_json('retail_info_data.json')[data_name]
    with pgsql['eats_retail_retail_parser'].dict_cursor() as cursor:
        cursor.execute('SELECT * FROM retail_info')
        actual_data = [row for row in cursor]

    for i, expected_elem in enumerate(expected_data):
        encrypted_elem = actual_data[i]

        retail_info = entities.RetailInfo(
            vendor_host=encrypted_elem['vendor_host'],
            client_id=encrypted_elem['client_id'],
            client_secret=encrypted_elem['client_secret'],
            scope=encrypted_elem['scope'],
            dek=encrypted_elem['dek'],
            id=0,
            retail_key='',
        )
        actual_elem = (
            await cron_context.retail_encryption.get_credentional_partner(
                retail_info,
            )
        )

        assert (
            encrypted_elem['place_group_id'] == expected_elem['place_group_id']
        )
        assert actual_elem['client_id'] == expected_elem['client_id']
        assert actual_elem['client_secret'] == expected_elem['client_secret']
        assert actual_elem['vendor_host'] == expected_elem['vendor_host']
        assert actual_elem['scope'] == expected_elem['scope']
