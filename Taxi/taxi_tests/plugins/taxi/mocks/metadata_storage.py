import pytest


class MetadataStorageMock:
    def __init__(self):
        # namespace -> id -> {value, updated}
        self._metadata = {}

    def get_metadata(self, namespace, meta_id):
        ns_data = self._metadata.get(namespace)
        if ns_data is None:
            return None
        return ns_data.get(meta_id)

    def add_metadata_value(self, namespace, meta_id, meta_value, updated):
        ns_data = self._metadata.setdefault(namespace, {})
        ns_data[meta_id] = {'value': meta_value, 'updated': updated}

    def add_metadata(self, metadata_array):
        for elem in metadata_array:
            self.add_metadata_value(
                elem['ns'], elem['id'], elem['value'], elem['updated'],
            )


def parse_marker(marker, metadata_storage, load_json):
    if 'filename' in marker.kwargs:
        in_file = load_json(marker.kwargs['filename'])
        for elem in in_file:
            metadata_storage.add_metadata([elem])
    else:
        metadata_storage.add_metadata(**marker.kwargs)


@pytest.fixture
def mock_metadata_storage(mockserver, request, load_json):
    metadata_storage = MetadataStorageMock()
    markers = request.node.get_marker('metadata_storage')
    if markers:
        for marker in markers:
            parse_marker(marker, metadata_storage, load_json)

    @mockserver.handler('/v1/metadata/store')
    def handler_store(request):
        return mockserver.make_response(
            status=201,
            json={'code': 'Created', 'message': 'Metadata is stored'},
        )

    @mockserver.json_handler('/v1/metadata/retrieve')
    def handler_retrieve(request):
        namespace = request.args.get('ns')
        meta_id = request.args.get('id')
        if namespace is None or meta_id is None:
            return mockserver.make_response(
                status=400,
                json={
                    'code': 'BadInputParams',
                    'message': (
                        'Input parameter is missing (ns, id are required)'
                    ),
                },
            )
        meta_value = metadata_storage.get_metadata(namespace, meta_id)
        if meta_value is None:
            return mockserver.make_response(
                status=404,
                json={
                    'code': 'MetadataNotFound',
                    'message': 'Perhaps you forgot to mock it',
                },
            )
        return meta_value

    return metadata_storage
