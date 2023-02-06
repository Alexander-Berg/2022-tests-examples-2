# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import operator

import pytest

from personal_caches_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _personal_phone_retrieve(request):
        request_json = request.json
        request_json['items'].sort(key=operator.itemgetter('id'))
        assert request_json['items'] == [
            {'id': 'phone_pd_id_1'},
            {'id': 'phone_pd_id_1'},
            {'id': 'phone_pd_id_11'},
            {'id': 'phone_pd_id_123'},
            {'id': 'phone_pd_id_2'},
        ]
        return {
            'items': [
                {'id': 'phone_pd_id_1', 'value': '+79998887766'},
                {'id': 'phone_pd_id_1', 'value': '+79998887766'},
                {'id': 'phone_pd_id_11', 'value': '+79998887777'},
                {'id': 'phone_pd_id_123', 'value': '+79998887766'},
                {'id': 'phone_pd_id_2', 'value': '+70001112233'},
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _personal_driver_license_retrieve(request):
        request_json = request.json
        request_json['items'].sort(key=operator.itemgetter('id'))
        assert request_json['items'] == [
            {'id': 'driver_license_pd_id_1'},
            {'id': 'driver_license_pd_id_1'},
            {'id': 'driver_license_pd_id_11'},
            {'id': 'driver_license_pd_id_123'},
            {'id': 'driver_license_pd_id_2'},
        ]
        return {
            'items': [
                {'id': 'driver_license_pd_id_1', 'value': 'LICENSE1'},
                {'id': 'driver_license_pd_id_1', 'value': 'LICENSE1'},
                {'id': 'driver_license_pd_id_11', 'value': 'LICENSE11'},
                {'id': 'driver_license_pd_id_123', 'value': 'LICENSE123'},
                {'id': 'driver_license_pd_id_2', 'value': 'LICENSE2'},
            ],
        }
