import pytest

YT_CRON_TABLE = '//home/test/cron_table'
EXPECTED_LAST_UPDATED_DATE = '2019-02-15T12:34:56'
EXPECTED_LAST_UPDATED_DATE_WITH_FAILED = '2019-02-14T12:34:56'
QUERY_GET_LAST_UPDATE = """SELECT last_updated FROM taxi_selfreg.sync_dates '
            'WHERE sync_name=\'selfreg_profiles\'"""


@pytest.mark.config(SELFREG_FAILED_TO_UPSERT_LEADS_PATH=YT_CRON_TABLE)
@pytest.mark.now('2021-11-24T12:00:00+0000')
async def test_sync_selfreg_profiles_continuously(
        cron_context,
        cron_runner,
        pgsql,
        mock_hiring_api_v2_leads_upsert,
        load_json,
        yt_client,
):
    # arrange
    hiring_api_static = load_json('mock_hiring_api.json')
    expected_yt_data = load_json('expected_yt_data.json')
    mock_hiring_api = mock_hiring_api_v2_leads_upsert(
        hiring_api_static['responses'],
    )

    # act
    await cron_runner.selfreg_profiles_sync()

    # assert
    assert mock_hiring_api.times_called == 3
    hiring_api_call = mock_hiring_api.next_call()
    data = hiring_api_call['request'].json
    data['lead'].get('extra', []).sort(key=lambda x: x['name'])
    data['assets'][0].get('extra', []).sort(key=lambda x: x['name'])
    assert data == hiring_api_static['expected_request']['driver_with_auto']

    hiring_api_call = mock_hiring_api.next_call()
    data = hiring_api_call['request'].json
    data['lead'].get('extra', []).sort(key=lambda x: x['name'])
    assert data == hiring_api_static['expected_request']['eats_courier_native']

    hiring_api_call = mock_hiring_api.next_call()
    data = hiring_api_call['request'].json
    data['lead'].get('extra', []).sort(key=lambda x: x['name'])
    data['assets'][0].get('extra', []).sort(key=lambda x: x['name'])
    assert data == hiring_api_static['expected_request']['not_chosen_flow']

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT last_updated FROM taxi_selfreg.sync_dates '
            'WHERE sync_name=\'selfreg_profiles\'',
        )
        assert (
            rows[0]['last_updated'].isoformat() == EXPECTED_LAST_UPDATED_DATE
        )

    yt_rows = list(yt_client.read_table(YT_CRON_TABLE))
    assert yt_rows[-1] == expected_yt_data


@pytest.mark.config(
    SELFREG_PROFILES_SYNC_CLAUSES=[
        {'name': 'chosen_flow', 'values': ['driver-with-auto']},
    ],
)
@pytest.mark.now('2021-11-24T12:00:00+0000')
async def test_sync_selfreg_profiles_with_included_filter(
        cron_context, cron_runner, mock_hiring_api_v2_leads_upsert, load_json,
):
    # arrange
    hiring_api_static = load_json('mock_hiring_api.json')
    mock_hiring_api = mock_hiring_api_v2_leads_upsert(
        [hiring_api_static['responses'][0]],
    )

    # act
    await cron_runner.selfreg_profiles_sync()

    # assert
    assert mock_hiring_api.times_called == 1
    hiring_api_call = mock_hiring_api.next_call()
    data = hiring_api_call['request'].json
    data['lead'].get('extra', []).sort(key=lambda x: x['name'])
    data['assets'][0].get('extra', []).sort(key=lambda x: x['name'])
    assert data == hiring_api_static['expected_request']['driver_with_auto']


@pytest.mark.config(
    SELFREG_PROFILES_SYNC_CLAUSES=[
        {
            'name': 'chosen_flow',
            'values': ['driver-with-auto'],
            'is_excludes': True,
        },
    ],
)
@pytest.mark.config(SELFREG_FAILED_TO_UPSERT_LEADS_PATH=YT_CRON_TABLE)
@pytest.mark.now('2021-11-24T12:00:00+0000')
async def test_sync_selfreg_profiles_with_excluded_filter(
        cron_context,
        cron_runner,
        mock_hiring_api_v2_leads_upsert,
        load_json,
        yt_client,
):
    # arrange
    hiring_api_static = load_json('mock_hiring_api.json')
    mock_hiring_api = mock_hiring_api_v2_leads_upsert(
        [hiring_api_static['responses'][0], hiring_api_static['responses'][2]],
    )

    # act
    await cron_runner.selfreg_profiles_sync()

    # assert
    assert mock_hiring_api.times_called == 2

    hiring_api_call = mock_hiring_api.next_call()
    data = hiring_api_call['request'].json
    data['lead'].get('extra', []).sort(key=lambda x: x['name'])
    assert data == hiring_api_static['expected_request']['eats_courier_native']

    hiring_api_call = mock_hiring_api.next_call()
    data = hiring_api_call['request'].json
    data['lead'].get('extra', []).sort(key=lambda x: x['name'])
    data['assets'][0].get('extra', []).sort(key=lambda x: x['name'])
    assert data == hiring_api_static['expected_request']['not_chosen_flow']


@pytest.mark.config(SELFREG_FAILED_TO_UPSERT_LEADS_PATH=YT_CRON_TABLE)
@pytest.mark.now('2021-11-24T12:00:00+0000')
async def test_sync_selfreg_profiles_too_many_requests(
        cron_context,
        cron_runner,
        pgsql,
        mock_hiring_api_v2_leads_upsert,
        load_json,
):
    # arrange
    hiring_api_static = load_json('mock_hiring_api.json')
    hiring_api_static['responses'][2] = hiring_api_static['failed_response']
    responses_with_failed = hiring_api_static['responses']
    mock_hiring_api_v2_leads_upsert(responses_with_failed)

    # act
    await cron_runner.selfreg_profiles_sync()

    # assert
    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT last_updated FROM taxi_selfreg.sync_dates '
            'WHERE sync_name=\'selfreg_profiles\'',
        )
        assert (
            rows[0]['last_updated'].isoformat()
            == EXPECTED_LAST_UPDATED_DATE_WITH_FAILED
        )
