import http

import pytest

from eats_integration_offline_orders.internal import constants
from test_eats_integration_offline_orders import conftest

HANDLER_NAME = '/admin/v1/posm/template'
HEADERS = {'Content-Type': 'application/pdf', 'X-File-Name': 'filename'}
DEFAULT_SUCCESS_RESPONSE = {'template_id': 1}
DEFAULT_NOT_FOUND_RESPONSE = {
    'code': 'not_found',
    'message': 'place not found: not_found_place',
}


@pytest.fixture(name='mock_mds_s3_put')
def _mock_mds_s3_put(mockserver):
    @mockserver.handler(
        rf'/mds_s3/{conftest.MDS_S3_BUCKET_NAME}/'
        rf'{constants.MDS_TEMPLATES_PREFIX}/(?P<file_id>\d+)',
        regex=True,
    )
    async def _mds_s3_mock(request, **kwargs):
        assert request.method == 'PUT'
        return mockserver.make_response(
            '<Body></Body>', headers={'ETag': 'asdf'},
        )


@pytest.mark.parametrize(
    ('expected_code', 'expected_response'),
    (
        pytest.param(
            http.HTTPStatus.OK,
            conftest.create_admin_posm_template(
                template_id=1,
                name='filename',
                description='',
                visibility='global',
                settings=conftest.ADMIN_TEMPLATE_AUTO_GENERATE_SETTINGS,
            ),
            id='OK',
        ),
    ),
)
async def test_admin_posm_template_add_global(
        taxi_eats_integration_offline_orders_web,
        mock_mds_s3_put,
        expected_code,
        expected_response,
):
    data = conftest.load_pdf_template('template.pdf')

    response = await taxi_eats_integration_offline_orders_web.post(
        HANDLER_NAME, data=data, headers=HEADERS,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response


async def test_admin_posm_template_add_bad_format(
        taxi_eats_integration_offline_orders_web, mockserver,
):
    response = await taxi_eats_integration_offline_orders_web.post(
        HANDLER_NAME, params={}, data=b'absolutely-not-pdf', headers=HEADERS,
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response', 'expected_db'),
    (
        pytest.param(
            {'place_ids': 'place_id__1'},
            http.HTTPStatus.OK,
            conftest.create_admin_posm_template(
                template_id=1,
                name='filename',
                description='',
                visibility='restaurant',
                place_ids=['place_id__1'],
                settings=conftest.ADMIN_TEMPLATE_AUTO_GENERATE_SETTINGS,
            ),
            [(1, 'place_id__1')],
            id='OK',
        ),
        pytest.param(
            {'place_ids': 'place_id__1,place_id__1'},
            http.HTTPStatus.OK,
            conftest.create_admin_posm_template(
                template_id=1,
                name='filename',
                description='',
                visibility='restaurant',
                place_ids=['place_id__1'],
                settings=conftest.ADMIN_TEMPLATE_AUTO_GENERATE_SETTINGS,
            ),
            [(1, 'place_id__1')],
            id='OK-few-same',
        ),
        pytest.param(
            {'place_ids': 'place_id__1,place_id__2'},
            http.HTTPStatus.OK,
            conftest.create_admin_posm_template(
                template_id=1,
                name='filename',
                description='',
                visibility='restaurant',
                place_ids=['place_id__1', 'place_id__2'],
                settings=conftest.ADMIN_TEMPLATE_AUTO_GENERATE_SETTINGS,
            ),
            [(1, 'place_id__1'), (1, 'place_id__2')],
            id='OK-few',
        ),
        pytest.param(
            {'place_ids': 'not_found_place'},
            http.HTTPStatus.NOT_FOUND,
            DEFAULT_NOT_FOUND_RESPONSE,
            [],
            id='not-found-place',
        ),
        pytest.param(
            {'place_ids': 'place_id__1,not_found_place'},
            http.HTTPStatus.NOT_FOUND,
            DEFAULT_NOT_FOUND_RESPONSE,
            [],
            id='few-one-not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_admin_posm_template_add_place(
        taxi_eats_integration_offline_orders_web,
        mock_mds_s3_put,
        pgsql,
        params,
        expected_code,
        expected_response,
        expected_db,
):
    data = conftest.load_pdf_template('template.pdf')
    response = await taxi_eats_integration_offline_orders_web.post(
        HANDLER_NAME, params=params, data=data, headers=HEADERS,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    cursor = pgsql['eats_integration_offline_orders'].cursor()
    cursor.execute(
        """
SELECT template_id, place_id
FROM restaurants_posm_templates
ORDER BY template_id, place_id
;
        """,
    )
    rows = cursor.fetchall()
    assert rows == expected_db
