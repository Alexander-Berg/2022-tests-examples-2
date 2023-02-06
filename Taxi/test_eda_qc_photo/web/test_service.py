import pickle

import pytest


@pytest.fixture
def taxi_eda_qc_photo_mocks(mockserver, open_file, pgsql):
    """Put your mocks here"""

    @mockserver.handler('/mds_s3', prefix=True)
    async def _mds_s3__handler(request):
        if request.method == 'PUT':
            return mockserver.make_response(
                headers={'Key': 'file-key', 'ETag': 'some-e-tag'},
            )
        if request.method == 'GET':
            with open_file('kitten-small.png', mode='rb', encoding=None) as fp:
                image = fp.read()
            return mockserver.make_response(
                response=image,
                content_type='image/png',
                headers={'Key': 'file-key', 'ETag': 'some-e-tag'},
            )

    @mockserver.json_handler('/mds_avatars', prefix=True)
    async def _mds_avatars__handler(request):
        return {
            'group-id': 1234,
            'sizes': {
                'big': {'width': 1, 'height': 1, 'path': '/path/to/file'},
            },
        }

    # just load some bin data, to check if we can use pickle
    cursor = pgsql['eda_qc_photo'].cursor()
    cursor.execute(
        """
        INSERT INTO qc_photo.conversation_data (name, key, data)
        VALUES (%s, %s, %s)
        """,
        ['qc_photo_loader', '379425963===379425963', pickle.dumps(0)],
    )


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_eda_qc_photo_mocks')
@pytest.mark.config(
    EDA_QC_PHOTO_BOT_SETTINGS={
        'developer_ids': [],
        'poll_interval': 0.5,
        'polling_enabled': True,
    },
)
async def test_ping(taxi_eda_qc_photo_web):
    response = await taxi_eda_qc_photo_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
