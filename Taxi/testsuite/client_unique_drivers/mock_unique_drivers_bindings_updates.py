import copy
import json

import pytest

_ONLY_CHECKED_DOCUMENTS = 'only_checked_documents'

_SERVICE = '/unique-drivers'
_V1_BINDING_UPDATED_URL = '/v1/bindings/updates'

# Usage: @pytest.mark.unique_drivers(
#            stream={
#             'licenses_by_unique_drivers': {
#                 'last_revision': '111112_1',
#                 'items': [
#                     {
#                         'id': 'driver1',
#                         'is_deleted': False,
#                         'revision': '111111_1',
#                         'data': {
#                             'license_ids': [
#                                 'license_1_1, license_1_2, license_1_3',
#                             ],
#                         },
#                     },
#                     ...
#                 ],
#             },
#             'license_by_driver_profile': {
#                 'last_revision': '779_2',
#                 'items': [
#                     {
#                         'id': 'park_driver1',
#                         'is_deleted': False,
#                         'revision': '777_1',
#                         'data': {'license_id': 'license_1_1'},
#                     },
#                     ...
#                 ],
#             },
#         }
#        )
_UNIQUE_DRIVERS_MARKER = 'unique_drivers'


class UniqueDriversContext:
    def __init__(self):
        self.stream = None

    def reset(self):
        self.stream = None

    def set_stream(self, stream):
        self.stream = stream

    def get_stream(self):
        return self.stream


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{_UNIQUE_DRIVERS_MARKER}: unique drivers',
    )


@pytest.fixture(name='bindings_updates_mock')
def _bindings_updates_mock(mockserver):
    unique_drivers_context = UniqueDriversContext()

    def _extract_revision(revision):
        return [int(x) for x in revision.split('_')]

    def _process_stream(stream, only_checked_documents, last_known_revision):
        if only_checked_documents:
            stream['items'] = stream['items'][:-1]

        if last_known_revision:
            last_known_ts = _extract_revision(last_known_revision)

            stream['items'] = [
                item
                for item in stream['items']
                if _extract_revision(item['revision']) > last_known_ts
            ]

        if stream['items']:
            stream['last_revision'] = stream['items'][-1]['revision']
        else:
            stream['last_revision'] = last_known_revision

    @mockserver.handler(_SERVICE + _V1_BINDING_UPDATED_URL)
    def _updates(request):
        last_revision_unique_drivers = request.args.get(
            'last_known_revision_unique_drivers',
        )
        last_revision_driver_profiles = request.args.get(
            'last_known_revision_driver_profiles',
        )
        only_checked_documents = (
            request.args.get(_ONLY_CHECKED_DOCUMENTS) is not None
        )

        stream = copy.deepcopy(unique_drivers_context.get_stream())

        _process_stream(
            stream['licenses_by_unique_drivers'],
            only_checked_documents,
            last_revision_unique_drivers,
        )
        _process_stream(
            stream['license_by_driver_profile'],
            only_checked_documents,
            last_revision_driver_profiles,
        )

        return mockserver.make_response(
            json.dumps(stream), 200, headers={'X-Polling-Delay-Ms': '100'},
        )

    return unique_drivers_context


@pytest.fixture(name='unique_drivers_fixture', autouse=True)
def _unique_drivers_fixture(bindings_updates_mock, request):
    bindings_updates_mock.reset()

    for marker in request.node.iter_markers(_UNIQUE_DRIVERS_MARKER):
        if marker.kwargs:
            bindings_updates_mock.set_stream(**marker.kwargs)

    yield bindings_updates_mock

    bindings_updates_mock.reset()
