import pytest

from taxi.conf import settings
from taxi.external import mds


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'image_file,image_id,response,status_code,exception', [
        # Happy path
        ('PNG', '1234/567-89ab-cdef', 'mds_ok.xml', 200, None),
        # Malformed response
        ('PNG', '1234/567-89ab-cdef', 'mds_invalid.xml', 200,
         mds.MDSInvalidResponse),
        # Internal server error
        ('PNG', '1234/567-89ab-cdef', None, 500, mds.MDSHTTPError)
    ]
)
@pytest.inline_callbacks
def test_mds_upload(image_file, image_id, response, status_code, exception,
                    areq_request, load, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        if status_code == 200:
            body = load(response).replace('IMAGE_ID', image_id)
            return areq_request.response(200, body=body)
        else:
            return areq_request.response(status_code, body=None)

    monkeypatch.setattr(
        settings, 'MDS_UPLOAD_HOST', 'http://mds'
    )

    if exception is None:
        result = yield mds.upload(image_file)
        assert result is not None
        assert result == image_id
    else:
        with pytest.raises(exception) as exc_info:
            yield mds.upload(image_file)
        assert isinstance(exc_info.value, exception)
        if exception == mds.MDSHTTPError:
            assert exc_info.value.status_code == status_code


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('image_id,status_code,exception', [
    # Happy path
    ('123/4567-89ab-cde', 200, None),
    # Image not found
    ('567/1234-89ab-cde', 404, mds.MDSHTTPError),
    # Internal server error
    ('567/1234-89ab-cde', 500, mds.MDSHTTPError)
])
@pytest.inline_callbacks
def test_mds_remove(image_id, status_code, exception,
                    areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(status_code, body=None)

    monkeypatch.setattr(
        settings, 'MDS_UPLOAD_HOST', 'http://mds'
    )

    if exception is None:
        result = yield mds.remove(image_id)
        assert result is None
    else:
        with pytest.raises(exception) as exc_info:
            yield mds.remove(image_id)

        assert isinstance(exc_info.value, exception)
        if exception == mds.MDSHTTPError:
            assert exc_info.value.status_code == status_code


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('image_id,status_code,result,exception', [
    # Happy path
    ('123/4567-89ab-cde', 200, True, None),
    # Image not found
    ('567/1234-89ab-cde', 404, False, None),
    # Internal server error
    ('567/1234-89ab-cde', 500, None, mds.MDSHTTPError)
])
@pytest.inline_callbacks
def test_mds_exists(image_id, status_code, result, exception,
                    areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(status_code, body=None)

    monkeypatch.setattr(
        settings, 'MDS_GET_HOST', 'http://mds'
    )

    if exception is None:
        actual_result = yield mds.exists(image_id)
        assert result == actual_result
    else:
        with pytest.raises(exception) as exc_info:
            yield mds.remove(image_id)

        assert isinstance(exc_info.value, exception)
        if exception == mds.MDSHTTPError:
            assert exc_info.value.status_code == status_code
