import json

import pytest


class TestUtils:
    def __init__(
            self,
            taxi_eats_nomenclature,
            update_taxi_config,
            load_json,
            mds_s3_storage,
    ):
        self._taxi_eats_nomenclature = taxi_eats_nomenclature
        self._update_taxi_config = update_taxi_config
        self._load_json = load_json
        self._mds_s3_storage = mds_s3_storage

    def config_set_upload_state(self, value):
        self._update_taxi_config(
            'EATS_NOMENCLATURE_UPLOAD_TO_VIEWER_SETTINGS',
            {'enable_vendor_data_upload': value},
        )

    def s3_get_single_file(self):
        return json.loads(
            list(self._mds_s3_storage.storage.items())[0][1].data,
        )

    @staticmethod
    def sorted_json_data(data):
        items = data['items']
        items.sort(key=lambda x: x['origin_id'])

        return data


@pytest.fixture
def test_utils(
        taxi_eats_nomenclature, update_taxi_config, load_json, mds_s3_storage,
):
    return TestUtils(
        taxi_eats_nomenclature, update_taxi_config, load_json, mds_s3_storage,
    )
