import http

import pytest

from quality_control import consts
from test_quality_control import utils as test_utils

URL = 'api/v1/pass/media'

DRIVER_PHOTO = 'driver-photo'
IDENTITY_CARD = 'identity-card'


async def init(qc_client, exam) -> str:
    # test initialization
    entity = dict(id='1', type='driver')

    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    return pass_id


@pytest.mark.parametrize(
    'store_mode',
    [
        consts.Switcher.OFF,
        consts.Switcher.DRYRUN,
        consts.Switcher.TRYOUT,
        consts.Switcher.ON,
    ],
)
async def test_media_storage(
        qc_app, qc_client, media_storage, mds_s3_client, store_mode,
):
    exam_code = 'identity'
    # store media files
    qc_app.config.QC_USE_MEDIA_STORAGE[exam_code] = dict(
        __default__=store_mode,
    )
    pass_id = await init(qc_client, exam_code)

    if store_mode != consts.Switcher.OFF:
        assert media_storage.get_size(IDENTITY_CARD) == 1
        assert media_storage.get_size(DRIVER_PHOTO) == 1
    else:
        assert not media_storage.get_size(IDENTITY_CARD)
        assert not media_storage.get_size(DRIVER_PHOTO)

    if store_mode != consts.Switcher.ON:
        assert mds_s3_client.size() == 3
    else:
        assert mds_s3_client.size() == 1

    await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='selfie'),
    )
    await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='title'),
    )
    await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='visa'),
    )

    assert not media_storage.get_size(IDENTITY_CARD)
    assert not media_storage.get_size(DRIVER_PHOTO)
    assert not mds_s3_client.size()


async def test_media_code_not_found(qc_app, qc_client):
    pass_id = await init(qc_client, 'identity')

    response = await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='unknown'),
    )

    assert response.status == 404
    assert (await response.json())['code'] == 'MEDIA_CODE_NOT_FOUND'


async def test_pass_not_found(qc_app, qc_client):
    response = await qc_client.delete(
        URL,
        params=dict(pass_id='507f191e810c19729de860ea', media_code='visa'),
    )

    assert response.status == 404
    assert (await response.json())['code'] == 'PASS_NOT_FOUND'


async def test_wrong_exam(qc_app, qc_client):
    pass_id = await init(qc_client, 'identity')

    response = await qc_client.delete(
        URL, params=dict(pass_id=pass_id, exam='dkvu', media_code='visa'),
    )

    assert response.status == 400
    assert (await response.json())['code'] == 'WRONG_EXAM_CODE'


async def test_delete_twice(qc_app, qc_client):
    pass_id = await init(qc_client, 'identity')

    response = await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='selfie'),
    )
    assert response.status == 200

    response = await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='selfie'),
    )
    assert response.status == 200


@pytest.mark.config(QC_USE_MEDIA_STORAGE=dict(identity=dict(__default__='on')))
async def test_already_removed_from_ms(qc_app, qc_client, media_storage):
    pass_id = await init(qc_client, 'identity')
    etags = media_storage.get_objects(DRIVER_PHOTO)
    for etag in etags:
        media_storage.delete_object(DRIVER_PHOTO, etag)

    response = await qc_client.delete(
        URL, params=dict(pass_id=pass_id, media_code='selfie'),
    )
    assert response.status == 200
