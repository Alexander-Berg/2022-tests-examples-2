import pytest


@pytest.mark.parametrize(
    'input,expected_code',
    [
        ({'user_id': 'id1', 'fingerprint': 'fingerprint1'}, 200),
        ({'user_id': 'id2'}, 400),
        ({'fingerprint': 'fingerprint3'}, 400),
    ],
)
def test_save_fingerprint_base(
        taxi_antifraud, mockserver, input, expected_code,
):
    @mockserver.handler('/s3mds/', prefix=True)
    def mock_mds(request):
        assert request.method == 'PUT'
        url = request.path.split('/')
        assert len(url) == 7
        assert url[2] == 'client'
        assert url[3] == 'user'
        assert url[4] == 'fingerprint'
        assert url[5] == 'full'
        assert url[6] == input['user_id']
        assert request.data.decode() == input['fingerprint']
        return mockserver.make_response('', 200)

    response = taxi_antifraud.post('client/user/save_fingerprint', json=input)

    if expected_code == 200:
        mock_mds.wait_call()

    assert response.status_code == expected_code
