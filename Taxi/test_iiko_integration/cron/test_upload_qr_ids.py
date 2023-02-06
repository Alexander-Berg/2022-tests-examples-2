import copy
from typing import Optional

import pytest

from iiko_integration.crontasks import upload_qr_ids as upload_qr_ids_task
from iiko_integration.generated.cron import run_cron
from test_iiko_integration import stubs


TABLE_PATH = '//home/taxi-iiko-integration/test_table'


def _get_config_with_duplicate_ids():
    config_copy = copy.deepcopy(stubs.CONFIG_RESTAURANT_INFO)
    rest_copy = copy.deepcopy(config_copy['restaurant01'])
    rest_copy['geosearch_id'] = '12345'
    for i in range(3):
        config_copy['other_restaurant' + str(i)] = rest_copy
    return config_copy


@pytest.mark.now('2020-06-11T00:00:00+00:00')
@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_INFO=stubs.CONFIG_RESTAURANT_INFO,
    IIKO_INTEGRATION_GEOSEARCH_QR_IDS_TABLE_PATH=TABLE_PATH,
)
@pytest.mark.parametrize(
    ('expected_rows', 'table_path', 'is_error'),
    (
        pytest.param(
            [
                {
                    'permalink': '1400568734',
                    'json': {'qr_id': 'restaurant01'},
                    'original_id': 'restaurant01',
                },
            ],
            TABLE_PATH,
            False,
            marks=pytest.mark.yt(static_table_data=['yt_test_table.yaml']),
            id='Success',
        ),
        pytest.param(
            None,
            TABLE_PATH + '42',
            False,
            marks=pytest.mark.config(
                IIKO_INTEGRATION_GEOSEARCH_QR_IDS_TABLE_PATH=TABLE_PATH + '42',
            ),
            id='Table not exists',
        ),
        pytest.param(
            [
                {
                    'permalink': '1400568734',
                    'json': {'qr_id': 'restaurant01'},
                    'original_id': 'restaurant01',
                },
            ],
            TABLE_PATH,
            True,
            marks=[
                pytest.mark.yt(static_table_data=['yt_test_table.yaml']),
                pytest.mark.config(
                    IIKO_INTEGRATION_RESTAURANT_INFO=(
                        _get_config_with_duplicate_ids()
                    ),
                ),
            ],
            id='Duplicate geosearch_id in config',
        ),
    ),
)
async def test(
        yt_apply,
        yt_client,
        expected_rows: Optional[list],
        table_path: str,
        is_error: bool,
):
    try:
        await run_cron.main(
            ['iiko_integration.crontasks.upload_qr_ids', '-t', '0'],
        )
        assert not is_error  # NotUniqueIdsError should raises
    except upload_qr_ids_task.NotUniqueIdsError:
        assert is_error  # NotUniqueIdsError should not raises

    if expected_rows is None:
        assert not yt_client.exists(table_path)
        return

    rows = list(yt_client.read_table(table_path))
    assert rows == expected_rows
