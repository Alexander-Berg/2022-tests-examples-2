import json

import pytest


@pytest.mark.parametrize(
    'input,mds_output,mds_expected_code,' 'output,expected_code',
    [
        (
            {'user_id': 'id1'},
            {'fingerprint': 'fingerprint1'},
            200,
            {'exists': True, 'fingerprint': 'fingerprint1'},
            200,
        ),
        ({'user_id': 'id2'}, {}, 404, {'exists': False}, 200),
    ],
)
def test_get_fingerprint_base(
        taxi_antifraud,
        mockserver,
        input,
        mds_output,
        mds_expected_code,
        output,
        expected_code,
):
    @mockserver.handler('/s3mds/', prefix=True)
    def mock_mds(request):
        assert request.method == 'GET'
        url = request.path.split('/')
        assert len(url) == 7
        assert url[2] == 'client'
        assert url[3] == 'user'
        assert url[4] == 'fingerprint'
        assert url[5] == 'full'
        assert url[6] == input['user_id']
        if mds_expected_code == 200:
            return mockserver.make_response(
                mds_output['fingerprint'], mds_expected_code,
            )
        return mockserver.make_response('', mds_expected_code)

    response = taxi_antifraud.post('client/user/get_fingerprint', json=input)
    assert response.status_code == expected_code
    data = json.loads(response.text)
    assert data == output
