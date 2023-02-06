import pytest

from test_taxi_exp.helpers import files


@pytest.mark.now('2020-01-09T12:00:00+0300')
async def test_metadata(taxi_exp_client):
    # non-mocked update trusted file
    response = await files.post_trusted_file(
        taxi_exp_client, 'taxi_phone_id', b'566afbe7ed2c89a5e03b049b\n',
    )
    assert response.status == 200

    # check metadata
    response = await files.get_trusted_file_metadata(
        taxi_exp_client, 'taxi_phone_id',
    )
    assert response.status == 200
    body = await response.json()
    body.pop('mds_id', None)
    body.pop('updated', None)
    assert body == {
        'tag': 'taxi_phone_id',
        'file_type': 'string',
        'file_format': 'string',
        'version': 1,
        'sha256': (
            '8d5c337bb6b4acd3e932f47d37909e1db7d360eb4bcd170172c16c8eeab79130'
        ),
        'file_size': 25,
        'lines': 1,
    }
