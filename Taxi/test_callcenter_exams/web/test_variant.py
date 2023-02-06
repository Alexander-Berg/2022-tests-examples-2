import pytest


HEADERS = {
    'Cookie': 'Session_id=123',
    'Content-Type': 'application/json',
    'X-Yandex-UID': '44',
}


@pytest.mark.parametrize(
    ['request_type', 'variant_id', 'questions', 'resp_code', 'resp'],
    [
        ('create', 'v_3', ['q_2', 'q_4'], 200, {}),
        (
            'create',
            'v_1',
            ['q_2', 'q_4'],
            400,
            {
                'code': 'DATABASE_QUERY_ERROR',
                'message': 'Attempt to insert existing variant',
            },
        ),
        (
            'create',
            'v_3',
            ['q_2', 'q_1000'],
            400,
            {
                'code': 'DATABASE_QUERY_ERROR',
                'message': (
                    'Attempt to insert unexisting question into variant'
                ),
            },
        ),
        (
            'modify',
            'v_3',
            ['q_2', 'q_4'],
            404,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Modification of uncreated variant',
            },
        ),
        ('modify', 'v_1', ['q_2', 'q_4'], 200, {}),
        (
            'modify',
            'v_1',
            ['q_2', 'q_1000'],
            400,
            {
                'code': 'DATABASE_QUERY_ERROR',
                'message': (
                    'Attempt to insert unexisting question into variant'
                ),
            },
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_create_modify_exam(
        web_app_client,
        pgsql,
        request_type,
        variant_id,
        questions,
        resp_code,
        resp,
):
    test_request = {'questions': questions}
    url = f'/v1/variant?id={variant_id}'

    if request_type == 'create':
        response = await web_app_client.post(
            url, json=test_request, headers=HEADERS,
        )
    if request_type == 'modify':
        response = await web_app_client.put(
            url, json=test_request, headers=HEADERS,
        )

    assert response.status == resp_code
    if resp != {}:
        assert await response.json() == resp

    if resp_code == 200:
        with pgsql['callcenter_exams'].cursor() as cursor:
            cursor.execute(
                f'SELECT questions FROM '
                f'callcenter_exams.exam_variants WHERE '
                f'variant_id=\'{variant_id}\'',
            )
            assert cursor.rowcount == 1
            res = cursor.fetchone()

            assert res[0] == questions


@pytest.mark.parametrize(
    ['variant_id', 'resp_code'], [('v_1', 200), ('v_3', 204)],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_delete_exam(web_app_client, pgsql, variant_id, resp_code):
    url = f'/v1/variant?id={variant_id}'

    response = await web_app_client.delete(url, headers=HEADERS)

    assert response.status == resp_code

    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            f'SELECT variant_id FROM '
            f'callcenter_exams.exam_variants WHERE '
            f'variant_id=\'{variant_id}\'',
        )
        assert cursor.rowcount == 0


@pytest.mark.parametrize(
    ['variant_id', 'resp_code', 'resp'],
    [
        ('v_1', 200, {'questions': ['q_1', 'q_2', 'q_3']}),
        (
            'v_3',
            404,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Request of unknown variant',
            },
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_get_exam(web_app_client, pgsql, variant_id, resp_code, resp):
    url = f'/v1/variant?id={variant_id}'

    response = await web_app_client.get(url, headers=HEADERS)

    assert response.status == resp_code
    assert await response.json() == resp
