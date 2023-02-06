import typing

import pytest


@pytest.fixture(name='passport_takeout', autouse=True)
def mock_passport_takeout(mockserver):
    class Context:
        def __init__(self):
            self.response_upload: typing.List[dict] = []
            self.response_upload_done: typing.List[dict] = []

        def mock_upload(self, status, status_code=200):
            self.response_upload.append(
                {'status': status, 'status_code': status_code},
            )

        def mock_upload_done(
                self, status, missing_files=None, status_code=200,
        ):
            obj = {'status': status, 'status_code': status_code}
            if missing_files is not None:
                obj['missing_files'] = missing_files
            self.response_upload_done.append(obj)

        @property
        def upload(self):
            return _mock_upload

        @property
        def upload_done(self):
            return _mock_upload_done

    context = Context()

    @mockserver.json_handler('takeout.passport/1/upload/', prefix=True)
    def _mock_upload(request):
        times_called = context.upload.times_called
        responses = context.response_upload

        if times_called >= len(responses):
            return {'status': 'ok'}

        response = responses[times_called]
        status_code = response.pop('status_code', 200)

        return mockserver.make_response(json=response, status=status_code)

    @mockserver.json_handler('takeout.passport/1/upload/done', prefix=True)
    def _mock_upload_done(request):
        times_called = context.upload_done.times_called
        responses = context.response_upload_done

        if times_called >= len(responses):
            return {'status': 'ok'}

        response = responses[times_called]
        status_code = response.pop('status_code', 200)

        return mockserver.make_response(json=response, status=status_code)

    return context
