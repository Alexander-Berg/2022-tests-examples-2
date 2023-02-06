# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import pytest

from device_notify_plugins import *  # noqa: F403 F401 I100


class FcmService:
    def __init__(self, mockserver):
        self._mockserver = mockserver

    # /iid/v1:batchAdd
    @staticmethod
    def on_register(request):
        return {'results': [{}]}

    # /iid/v1:batchRemove
    @staticmethod
    def on_unregister(request):
        return {'results': [{}]}

    # pylint: disable=too-many-return-statements
    # /fcm/send
    # if `collector` is specified, it should be a list,
    # where some data from request will be stored for analysis
    def on_send(self, request, collector=None):
        bdata = request.get_data()
        if len(bdata) > 4096:
            # GoogleApis returns just "MessageTooBig"
            return self._mockserver.make_response(
                '{"error": "MessageTooBig"}', 400,
            )
        jdata = json.loads(bdata.decode('utf-8'))
        # print(">>>>>", jdata)

        # message to topics, up to 5
        if 'condition' in jdata:
            if collector is not None:
                collector.append({'condition': jdata['condition']})
            return {'message_id': 6212382472385364521}
        # message to topic or exact device
        if 'to' in jdata:
            if collector is not None:
                collector.append({'to': jdata['to']})
            if jdata['to'].startswith('/topics/'):
                return {'message_id': 6212382472385364522}
            if '/' not in jdata['to']:
                return {
                    'multicast_id': 6212382472385364523,
                    'success': 1,
                    'failure': 0,
                    'canonical_ids': 0,
                    'results': [
                        {
                            'message_id': (
                                '0:2547475151911802%%' '41bd5c9637bd1c96'
                            ),
                        },
                    ],
                }
            return self._mockserver.make_response(
                '{"error": "invalid-to-field"}', 400,
            )
        # multicast message, up to 1000 of ids
        if 'registration_ids' in jdata:
            if collector is not None:
                collector.append(
                    {'registration_ids': jdata['registration_ids']},
                )
            id_count = len(jdata['registration_ids'])
            if id_count < 1 or id_count > 1000:
                return self._mockserver.make_response(
                    '{"error": "bad-ids-count"}', 400,
                )
            result = {
                'multicast_id': 6768162785295122557,
                'success': id_count,
                'failure': 0,
                'canonical_ids': 0,
                'results': [],
            }
            for _i in range(id_count):
                result['results'].append(
                    {'message_id': '0:2547475151911802%%41bd5c9637bd1c96'},
                )
            return result
        return self._mockserver.make_response(
            '{"error": "no-recipients-or-topics"}', 400,
        )


@pytest.fixture
def fcm_service(mockserver):
    return FcmService(mockserver)
