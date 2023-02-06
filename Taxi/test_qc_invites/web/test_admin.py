import pytest

from test_qc_invites.helpers import consts
from test_qc_invites.helpers import fixtures
from test_qc_invites.helpers import mocks


async def setup_dkk_call(taxi_qc_invites_web, mockserver, body, license_pd_id):
    # mock personal client
    mocks.mock_personal_license_find(mockserver, license_pd_id)
    response = await taxi_qc_invites_web.post(consts.INVITE_URL, json=body)
    return response


async def test_call_conflict(taxi_qc_invites_web, mockserver, pgsql):
    mocks.mock_personal_license_find(mockserver, '777')
    body = {
        'exam': 'dkk',
        'sanctions': ['orders_off'],
        'filters': {'car_number': 'x124yy777'},
        'comment': 'Комментарий',
    }
    for _ in range(2):
        response = await taxi_qc_invites_web.post(
            consts.INVITE_URL,
            json=body,
            headers={'X-Idempotency-Token': '666'},
        )
        assert response.status == 200

    cursor = pgsql['qc_invites'].cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM invites.filters
        GROUP BY id
    """,
    )
    assert cursor.fetchone()[0] == 1


@pytest.mark.config(QC_INVITES_BLOCKED_EXAMS=['dkk'])
async def test_invite_blocked_exam(taxi_qc_invites_web, pgsql):
    exam = 'dkk'
    body = dict(
        exam=exam, filters=dict(car_number='x124yy777'), comment='Комментарий',
    )
    response = await taxi_qc_invites_web.post(consts.INVITE_URL, json=body)
    assert response.status == 400
    assert await response.json() == dict(
        text=f'Exam {exam} is blocked by config',
    )

    cursor = pgsql['qc_invites'].cursor()
    cursor.execute(
        """
        SELECT c.exam, c.sanctions, c.media, c.reason, c.comment
        FROM invites.invites as c
    """,
    )

    assert not list(cursor)


@pytest.mark.parametrize(['body'], fixtures.TEST_INVITE_SUCCESS_BODY)
@pytest.mark.parametrize(['exam'], fixtures.TEST_INVITE_SUCCESS_EXAM)
async def test_invite(taxi_qc_invites_web, pgsql, body, exam, mockserver):
    license_pd_id = '777'
    body['exam'] = exam
    response = await setup_dkk_call(
        taxi_qc_invites_web=taxi_qc_invites_web,
        mockserver=mockserver,
        body=body,
        license_pd_id=license_pd_id,
    )
    assert response.status == 200

    cursor = pgsql['qc_invites'].cursor()

    cursor.execute(
        """
        SELECT c.exam, c.sanctions, c.media, c.reason, c.comment
        FROM invites.invites as c
    """,
    )

    # проверяем, что информация о вызове сохранила
    res = list(cursor)[0]
    assert exam == res[0]
    assert body['sanctions'] == res[1]
    assert body.get('media') == res[2]
    assert body.get('comment') == res[4]

    cursor.execute(
        """
            SELECT f.key, f.value
            FROM invites.invites as c
            LEFT JOIN invites.filters as f on (c.id = f.invite_id)
        """,
    )
    res = list(cursor)
    if body.get('park_id'):
        body['filters'].update({'park_id': body['park_id']})
    # Если в фильтрах запроса был передан номер ВУ, проверяем
    # что он заменён на licence_pd_id
    if body['filters'].get('license_number'):
        body['filters']['license_pd_id'] = license_pd_id
        del body['filters']['license_number']
    assert dict(res) == body['filters']


@pytest.mark.parametrize(['body'], fixtures.TEST_INVITE_SUCCESS_BODY)
@pytest.mark.parametrize(['exam'], fixtures.TEST_INVITE_SUCCESS_EXAM)
async def test_find(taxi_qc_invites_web, body, exam, mockserver):
    license_pd_id = '777'
    body['exam'] = exam
    response = await setup_dkk_call(
        taxi_qc_invites_web=taxi_qc_invites_web,
        mockserver=mockserver,
        body=body,
        license_pd_id=license_pd_id,
    )
    assert response.status == 200

    response = await taxi_qc_invites_web.post(
        consts.FIND_URL, json={'filter': {}},
    )
    res = await response.json()
    assert 'items' in res
    assert len(res['items']) == 1


@pytest.mark.parametrize(['body'], fixtures.TEST_INVITE_INFO_BODY)
async def test_invite_info(taxi_qc_invites_web, body, mockserver):
    license_pd_id = '777'
    response = await setup_dkk_call(
        taxi_qc_invites_web=taxi_qc_invites_web,
        mockserver=mockserver,
        body=body,
        license_pd_id=license_pd_id,
    )
    assert response.status == 200
    invite_id = (await response.json())['invite_id']

    # чекаем состояние вызова
    response = await taxi_qc_invites_web.get(
        consts.INVITE_INFO_URL,
        params={'invite_id': invite_id},
        headers={'X-Yandex-Uid': 'Zhora'},
    )
    assert response.status == 200
    data = await response.json()
    assert data['exam'] == body['exam']
    assert data['sanctions'] == body['sanctions']
    assert data['comment'] == body['comment']


async def test_settings(taxi_qc_invites_web):
    response = await taxi_qc_invites_web.get(
        consts.SETTINGS_URL, headers={'Accept-Language': 'ruRu'},
    )
    assert response.status == 200
