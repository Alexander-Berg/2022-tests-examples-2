import pytest

MY_SESSION_ID = 'c642b150-759a-4679-b614-52c8d7bc485d'
TANYA_CALL_GUID = 'TANYA-CALL-GUID'


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    class FakeMdsClient:
        storage = bytearray(b'WAV FILE MOCK')

        def get_object(self, key) -> bytearray:
            assert key.startswith('/TAXI/records/'), key
            return self.storage

    client = FakeMdsClient()
    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    @mockserver.handler(
        f'/TAXI/records/{MY_SESSION_ID}_phase_1_both.wav', prefix=True,
    )
    def _mock_all(request):
        if request.method == 'GET':
            data = mds_s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)


@pytest.fixture(name='tanya_s3_storage', autouse=True)
def _tanya_s3_storage():
    class FakeMdsClient:
        storage = bytearray(b'WAV FILE MOCK')

        def get_object(self, key) -> bytearray:
            if TANYA_CALL_GUID in key:
                return self.storage
            return bytearray(b'')

    client = FakeMdsClient()
    return client


@pytest.fixture(name='tanya_s3', autouse=True)
def _tanya_s3(mockserver, tanya_s3_storage):
    @mockserver.handler(f'{TANYA_CALL_GUID}.wav', prefix=True)
    def _mock_all(request):
        if request.method == 'GET':
            data = tanya_s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)


async def test_200(taxi_ivr_dispatcher, mockserver):

    params = {'session_id': MY_SESSION_ID}

    response = await taxi_ivr_dispatcher.get(
        '/cc/v1/ivr-dispatcher/v1/recordings', params=params,
    )

    assert response.status == 200, response.text


async def test_tanya_200(taxi_ivr_dispatcher, mockserver):
    @mockserver.handler(
        f'/TAXI/records/TANYA-CALL-GUID_phase_1_both.wav', prefix=True,
    )
    def _mock_all(request):
        return mockserver.make_response(None, 404)

    params = {'session_id': TANYA_CALL_GUID}

    response = await taxi_ivr_dispatcher.get(
        '/cc/v1/ivr-dispatcher/v1/recordings', params=params,
    )

    assert response.status == 200, response.text


async def test_404(taxi_ivr_dispatcher, mockserver):
    @mockserver.handler(
        f'/TAXI/records/NO_SESSION_ID_phase_1_both.wav', prefix=True,
    )
    def _mock_octo(request):
        return mockserver.make_response(None, 404)

    @mockserver.handler(f'NO_SESSION_ID.wav', prefix=True)
    def _mock_tanya(request):
        return mockserver.make_response(None, 404)

    params = {'session_id': 'NO_SESSION_ID'}

    response = await taxi_ivr_dispatcher.get(
        '/cc/v1/ivr-dispatcher/v1/recordings', params=params,
    )

    assert response.status == 404
