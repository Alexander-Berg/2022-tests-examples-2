import pytest

from test_callcenter_exams import conftest
from test_callcenter_exams.web.static.default import (
    passport_responses as blackbox,
)  # noqa  # pylint: disable=line-too-long


@pytest.mark.parametrize(
    ['url', 'request_data', 'handler', 'body'],
    [
        (
            '/cc/v1/callcenter-exams/form/v1/orders/draft',
            {
                'payment': {'payment_method_id': 'cash', 'type': 'cash'},
                'requirements': {'nosmoking': True, 'yellowcarnumber': True},
                'route': [{'val': 'some_val'}],
                'class': ['econom'],
            },
            'ordersdraft',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_handler(
        web_app_client, pgsql, url, request_data, handler, body,
):

    test_request = {'exam_data': {'question_id': 'q_1', 'exam_id': 'exam_1'}}

    test_request.update(request_data)

    response = await web_app_client.post(
        url,
        json=test_request,
        headers=conftest.pasport_headers(body['uid']['value']),
    )

    assert response.status == 200
    assert await response.json() == f'q_1_{handler}_resp'

    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            'SELECT question_stat FROM callcenter_exams.questions_pass '
            'WHERE exam_id=\'exam_1\' and question_id=\'q_1\'',
        )
        assert cursor.rowcount == 1
        assert cursor.fetchone()[0][handler] == request_data
