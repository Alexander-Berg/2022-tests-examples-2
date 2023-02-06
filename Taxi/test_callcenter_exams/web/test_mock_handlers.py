import pytest

from test_callcenter_exams import conftest
from test_callcenter_exams.web.static.default import (
    passport_responses as blackbox,
)  # noqa  # pylint: disable=line-too-long


@pytest.mark.parametrize(
    ['url', 'exam_id', 'question_id', 'resp', 'body'],
    [
        (
            '/cc/v1/callcenter-exams/form/v1/expecteddestinations',
            'exam_1',
            'q_1',
            'q_1_expecteddestinations_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/expectedpositions',
            'exam_1',
            'q_1',
            'q_1_expectedpositions_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/orders/commit',
            'exam_1',
            'q_1',
            'q_1_orderscommit_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/orders/search',
            'exam_1',
            'q_1',
            'q_1_orderssearch_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/paymentmethods',
            'exam_1',
            'q_1',
            'q_1_paymentmethods_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/profile',
            'exam_1',
            'q_1',
            'q_1_profile_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/zoneinfo',
            'exam_1',
            'q_1',
            'q_1_zoneinfo_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/nearestzone',
            'exam_1',
            'q_1',
            'q_1_nearestzone_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/orders/estimate',
            'exam_1',
            'q_1',
            'q_1_ordersestimate_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/zonaltariffdescription',
            'exam_1',
            'q_1',
            'q_1_zonaltariffdescription_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/preorder/avaliable',
            'exam_1',
            'q_1',
            'q_1_availability_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/orders/cancel',
            'exam_1',
            'q_1',
            None,
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/orders/estimate',
            'exam_1',
            'q_1',
            'q_1_ordersestimate_resp',
            blackbox.PASSPORT_RESPONSE_USER_1,
        ),
        (
            '/cc/v1/callcenter-exams/form/v1/expecteddestinations',
            'exam_2',
            'q_2',
            'default_expecteddestinations_resp',
            blackbox.PASSPORT_RESPONSE_USER_2,
        ),
        # Demo mode
        (
            '/cc/v1/callcenter-exams/form/v1/orders/cancel',
            'demo_exam',
            'q_1',
            None,
            blackbox.PASSPORT_RESPONSE_USER_2,
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_handler(web_app_client, url, exam_id, question_id, resp, body):

    test_request = {
        'exam_data': {'question_id': question_id, 'exam_id': exam_id},
        'some_param': 'aaaa',
    }

    response = await web_app_client.post(
        url,
        json=test_request,
        headers=conftest.pasport_headers(body['uid']['value']),
    )

    if url != '/cc/v1/callcenter-exams/form/v1/orders/estimate':
        assert response.status == 200
        assert await response.json() == resp
    else:
        # special request needed, 400 expected because of wrong request
        assert response.status == 400


@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_zoneinfo_admin(web_app_client):
    resp = 'q_1_zoneinfo_resp'

    test_request = {}

    url = '/v1/zoneinfo_admin/'

    response = await web_app_client.post(
        url, json=test_request, headers=conftest.pasport_headers('44'),
    )

    assert await response.json() == resp
