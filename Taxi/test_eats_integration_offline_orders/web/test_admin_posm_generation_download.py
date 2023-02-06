import http
import io
import zipfile

import pytest

from eats_integration_offline_orders.internal import constants
from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_files'),
    (
        pytest.param(
            {'generation_id': 2},
            http.HTTPStatus.OK,
            {
                'posm/generated/2/1/table_uuid__1_1.pdf',
                'posm/generated/2/1/table_uuid__2_2.pdf',
            },
            id='OK',
        ),
        pytest.param(
            {'generation_id': 1},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='invalid-status',
        ),
        pytest.param(
            {'generation_id': 3},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='invalid-status-2',
        ),
        pytest.param(
            {'generation_id': 4},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='deleted-generation',
        ),
        pytest.param(
            {'generation_id': 100500},
            http.HTTPStatus.NOT_FOUND,
            None,
            id='not-found-generation',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
        'posm_generations.sql',
        'posm_generations_templates.sql',
    ],
)
async def test_admin_posm_generation_download(
        taxi_eats_integration_offline_orders_web,
        mockserver,
        params,
        expected_code,
        expected_files,
):
    data = conftest.load_pdf_template('template.pdf')

    @mockserver.handler(
        rf'/mds_s3/{conftest.MDS_S3_BUCKET_NAME}/'
        rf'{constants.MDS_POSM_PREFIX}/(?P<file_id>.*)',
        regex=True,
    )
    async def _mds_s3_mock(request, **kwargs):
        assert request.method == 'GET'
        return mockserver.make_response(data, headers={'ETag': 'asdf'})

    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/posm/generation/download', params=params,
    )
    assert response.status == expected_code
    if expected_code is not http.HTTPStatus.OK:
        return
    body = await response.read()
    with io.BytesIO(body) as file:
        archive = zipfile.ZipFile(file)
        files = set(x.filename for x in archive.filelist)
    assert files == expected_files
