import http

from quality_control import consts
from test_quality_control import utils as test_utils


X_YANDEX_LOGIN = 'yamishanya'


async def test_default_data(qc_app, qc_client, media_storage, avatars_mds):
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'dkvu'
    await test_utils.prepare_entity(
        qc_client,
        entity['type'],
        entity['id'],
        data=dict(license_pd_id='license', name='Mishanya'),
    )

    qc_app.config.QC_USE_MEDIA_STORAGE[exam_code] = dict(
        __default__=consts.Switcher.ON,
    )

    # назначаем стандартное прохождение ДКВУ
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={
            'present': {'can_pass': True, 'sanctions': ['orders_off']},
            'pass': {'media': ['front', 'back']},
        },
    )
    assert response.status == http.HTTPStatus.OK

    # загружаем медиа
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    await test_utils.send_fake(qc_client, state)

    await test_utils.check_watermarks(qc_client, state, X_YANDEX_LOGIN)
