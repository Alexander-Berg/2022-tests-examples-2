import http

import pytest

from quality_control import consts
from test_quality_control import utils as test_utils

URL = '/api/v1/pass'


@pytest.mark.parametrize(
    'store_mode, read_mode',
    [
        (consts.Switcher.OFF, consts.Switcher.OFF),
        (consts.Switcher.OFF, consts.Switcher.DRYRUN),
        (consts.Switcher.OFF, consts.Switcher.TRYOUT),
        (consts.Switcher.OFF, consts.Switcher.ON),
        (consts.Switcher.DRYRUN, consts.Switcher.OFF),
        (consts.Switcher.DRYRUN, consts.Switcher.DRYRUN),
        (consts.Switcher.DRYRUN, consts.Switcher.TRYOUT),
        (consts.Switcher.DRYRUN, consts.Switcher.ON),
        (consts.Switcher.TRYOUT, consts.Switcher.OFF),
        (consts.Switcher.TRYOUT, consts.Switcher.DRYRUN),
        (consts.Switcher.TRYOUT, consts.Switcher.TRYOUT),
        (consts.Switcher.TRYOUT, consts.Switcher.ON),
        (consts.Switcher.ON, consts.Switcher.TRYOUT),
        (consts.Switcher.ON, consts.Switcher.ON),
        # Tests with from 'ON' to 'OFF' or 'DRYRUN' will be failed.
        # No way to turn back from 'ON' mode
    ],
)
async def test_media_storage(
        qc_app,
        qc_client,
        qc_cache,
        media_storage,
        mds_s3_client,
        store_mode,
        read_mode,
):
    # test initialization
    entity = {'id': '1', 'type': 'driver'}
    exam_code = 'identity'
    await test_utils.prepare_entity(qc_client, entity['type'], entity['id'])

    # store media files
    qc_app.config.QC_USE_MEDIA_STORAGE[exam_code] = dict(
        __default__=store_mode,
    )
    response = await qc_client.post(
        '/api/v1/state',
        params={'type': entity['type'], 'id': entity['id'], 'exam': exam_code},
        json={'present': {'can_pass': True, 'sanctions': ['orders_off']}},
    )
    assert response.status == http.HTTPStatus.OK
    state = await test_utils.check_state(
        qc_client, entity['type'], entity['id'], exam_code,
    )
    pass_id = state['present']['pass']['id']
    await test_utils.send_fake(qc_client, state)

    # retrieve pass with urls to media content
    qc_app.config.QC_USE_MEDIA_STORAGE[exam_code] = dict(__default__=read_mode)
    pass_item = await test_utils.check_pass(qc_client, pass_id, with_urls=True)

    # check retrieved media information
    media_settings = qc_cache.entity_settings(entity['type'])['exams'][
        exam_code
    ]['media']['items']
    for media in pass_item['media']:
        ms_settings = media_settings[media['code']].get('storage_settings')

        # check if media uploaded to media-storage
        storage = media.get('storage')
        if ms_settings and store_mode != consts.Switcher.OFF:
            assert storage['bucket'] == ms_settings['bucket']
            assert storage['type'] == 'media_storage'
            assert media_storage.get_etag(storage['id']) == storage['version']
        else:
            assert not storage

        # Check resulting url
        # remove common mds prefix
        url = media['url'][len('http://s3.mdst.yandex.net/') :]
        mds_bucket, url = url.split('/', 1)
        expected_mds_url = 'pass/{}/{}/{}/{}.jpg'.format(
            entity['type'], entity['id'], pass_id, media['code'],
        )
        if (
                ms_settings
                and store_mode != consts.Switcher.OFF
                and read_mode in [consts.Switcher.TRYOUT, consts.Switcher.ON]
        ):
            assert mds_bucket == 'media-storage'
            assert url == '{}/{}'.format(storage['bucket'], storage['version'])
            assert media_storage.get_object(
                storage['bucket'], storage['version'],
            )
        else:
            assert mds_bucket == 'attachments'
            assert url == expected_mds_url
            assert mds_s3_client.has_object(expected_mds_url)

        # check if content uploaded to mds
        if not ms_settings or store_mode != consts.Switcher.ON:
            assert mds_s3_client.has_object(expected_mds_url)
        else:
            assert not mds_s3_client.has_object(expected_mds_url)
