import json

import pytest

from .. import setters


class TestUtils:
    def __init__(
            self,
            taxi_eats_nomenclature,
            pg_cursor,
            update_taxi_config,
            load_json,
            mds_s3_storage,
    ):
        self._taxi_eats_nomenclature = taxi_eats_nomenclature
        self._update_taxi_config = update_taxi_config
        self._load_json = load_json
        self._mds_s3_storage = mds_s3_storage

        self.sql = setters.SqlSetter(pg_cursor)

    def config_set_upload_state(self, value):
        self._update_taxi_config(
            'EATS_NOMENCLATURE_UPLOAD_TO_VIEWER_SETTINGS',
            {'enable_categories_upload': value},
        )

    def s3_get_single_file(self):
        return json.loads(
            list(self._mds_s3_storage.storage.items())[0][1].data,
        )

    def s3_get_single_category(self):
        return self.s3_get_single_file()['categories'][0]

    @staticmethod
    def sorted_json_data(data):
        categories = data['categories']
        categories.sort(key=lambda x: x['id'])
        for category in categories:
            category['images'].sort(key=lambda x: x['url'])
            category['products'].sort(key=lambda x: x['id'])
            if 'tags' in category:
                category['tags'].sort()

        return data

    @staticmethod
    def verify_json_field(data, expected_data):
        for value_path, expected_value in expected_data.items():
            split_path = value_path.split('/')
            value = data
            for i in split_path:
                value = value.get(i)
            if isinstance(expected_value, list):
                assert sorted(value) == sorted(expected_value)
            else:
                assert value == expected_value


@pytest.fixture
def nmn_vwr_utils(
        taxi_eats_nomenclature,
        pg_cursor,
        update_taxi_config,
        load_json,
        mds_s3_storage,
):
    return TestUtils(
        taxi_eats_nomenclature,
        pg_cursor,
        update_taxi_config,
        load_json,
        mds_s3_storage,
    )
