# flake8: noqa
# pylint: disable=import-error,wildcard-import

import os
import pytest
import shutil
import yatest.common

from tests_market_hide_offers_rt import utils

API = '/v1/internal/load_mmap'


@pytest.fixture()
def teardown():
    yield
    path = yatest.common.work_path() + '/' + utils.DIR
    if os.path.exists(path):
        shutil.rmtree(path)


# Check internal api to create mmap file with valid arguments expect 200
async def test_internal_api_prepare_test_data(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID1, utils.YABS_ID1)], taxi_market_hide_offers_rt,
    )


# Check internal api to load mmap file with invalid arguments expect 400
async def test_internal_api_load_mmap_with_invalid_file(
        taxi_market_hide_offers_rt, teardown,
):
    response = await taxi_market_hide_offers_rt.post(API, json={'path': ''})

    assert response.status_code == 400


# Check internal api to load mmap file with valid arguments expect 200
async def test_internal_api_load_mmap_with_valid_file(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID1, utils.YABS_ID1)], taxi_market_hide_offers_rt,
    )

    path = yatest.common.work_path() + '/' + utils.DIR + '/' + utils.MMAP_FILE

    response = await taxi_market_hide_offers_rt.post(API, json={'path': path})

    assert response.status_code == 200
