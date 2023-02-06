# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest
from unique_drivers_plugins import *  # noqa: F403 F401


@pytest.fixture(name='personal', autouse=True)
def mock_personal(mockserver):
    def _bulk_store(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append(
                {'id': i['value'] + '_ID', 'value': i['value']},
            )
        return result

    def _bulk_retrieve_phones(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append(
                {'id': i['id'], 'value': '7950500505' + i['id'][-1]},
            )
        return result

    def _bulk_retrieve(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append({'id': i['id'], 'value': i['id'][:-3]})
        return result

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_store')
    def _licenses_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        return _bulk_retrieve_phones(request)

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _licenses_bulk_retrieve(request):
        return _bulk_retrieve(request)


@pytest.fixture(name='quality_control', autouse=True)
def mock_quality_control(mockserver):
    @mockserver.json_handler('/quality-control/api/v1/data/confirmed')
    def _data_confirmed(request):
        exam = request.args['exam']
        entity_id = request.args['id']
        entity_type = request.args['type']
        return {'pass_id': exam + '_' + entity_id + '_' + entity_type}


@pytest.fixture(name='logbroker')
def logbroker(testpoint):
    class Context:
        def __init__(self):
            self.publish_data = []

            @testpoint('logbroker_publish')
            def commit(data):  # pylint: disable=W0612
                self.publish_data.append(
                    {'data': json.loads(data['data']), 'name': data['name']},
                )

            self.commit_testpoint = commit

        @property
        def data(self):
            return self.publish_data[:]

        async def wait_publish(self, timeout=10):
            return await self.commit_testpoint.wait_call(timeout)

    return Context()
