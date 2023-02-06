import http

import pytest

from eats_integration_offline_orders.internal import constants
from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    ('params', 'expected_code'),
    (
        pytest.param({'template_id': 1}, http.HTTPStatus.OK, id='OK'),
        pytest.param(
            {'template_id': 3},
            http.HTTPStatus.NOT_FOUND,
            id='already-deleted',
        ),
        pytest.param(
            {'template_id': 4},
            http.HTTPStatus.OK,
            id='OK-already-deleted-links',
        ),
        pytest.param(
            {'template_id': 100500}, http.HTTPStatus.NOT_FOUND, id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'posm_templates.sql',
        'restaurants_posm_templates.sql',
    ],
)
async def test_admin_posm_template_delete(
        taxi_eats_integration_offline_orders_web,
        mockserver,
        pgsql,
        params,
        expected_code,
):
    s3_called = False

    @mockserver.handler(
        rf'/mds_s3/{conftest.MDS_S3_BUCKET_NAME}/'
        rf'{constants.MDS_TEMPLATES_PREFIX}/(?P<file_id>\d+)',
        regex=True,
    )
    async def _mds_s3_mock(request, **kwargs):
        nonlocal s3_called
        s3_called = True
        assert request.method == 'DELETE'
        assert request.path.endswith(
            f'{constants.MDS_TEMPLATES_ID}/{params["template_id"]}',
        )
        return mockserver.make_response(
            '<Body></Body>', headers={'ETag': 'asdf'},
        )

    response = await taxi_eats_integration_offline_orders_web.delete(
        '/admin/v1/posm/template', params=params,
    )
    assert response.status == expected_code
    cursor = pgsql['eats_integration_offline_orders'].cursor()
    cursor.execute(
        f"""
SELECT deleted_at
FROM posm_templates
WHERE id = {params["template_id"]}
;
        """,
    )
    rows = cursor.fetchall()
    assert rows is None or all(row is not None for row in rows)

    cursor.execute(
        f"""
SELECT deleted_at
FROM restaurants_posm_templates
WHERE template_id = { params["template_id"] }
;
        """,
    )
    rows = cursor.fetchall()
    assert rows is None or all(row is not None for row in rows)
    if expected_code == http.HTTPStatus.OK:
        assert s3_called
