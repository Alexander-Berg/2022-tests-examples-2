import pytest

from taxi.external import metadata_storage


@pytest.inline_callbacks
def test_metadata_retrieve_happy_path(areq_request):
    @areq_request
    def _v1_metadata_retrieve(method, url, **kwargs):
        assert method == 'POST'
        assert url.endswith('v1/metadata/retrieve')
        assert kwargs['params'] == {'try_archive': True, 'id': 'id', 'ns': 'ns'}
        return 200, '{}'

    response = yield metadata_storage.v1_metadata_retrieve(
        'id', 'ns', try_archive=True,
    )
    assert response == {}


@pytest.mark.parametrize(
    'status, expected_error', [
        (400, metadata_storage.ClientError),
        (500, metadata_storage.ServerError),
    ]
)
@pytest.inline_callbacks
def test_metadata_retrieve_unhappy_path(status, expected_error, areq_request):
    @areq_request
    def _v1_metadata_retrieve(method, url, **kwargs):
        return status, '{}'

    with pytest.raises(expected_error):
        yield metadata_storage.v1_metadata_retrieve(
            'id', 'ns', try_archive=True,
        )
