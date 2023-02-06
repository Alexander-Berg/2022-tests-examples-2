# pylint: disable=import-only-modules
import datetime
import json

import pytest

from .utils import select_named

INITIAL_TAGS = [
    {
        'id': 1,
        'driver_id': '(dbid1,uuid1)',
        'merge_policy': 'append',
        'tags': ['reposition_offer_sent'],
        'created_at': datetime.datetime(2020, 5, 18, 12, 0, 0),
        'until': datetime.datetime(2020, 5, 18, 15, 0, 0),
    },
    {
        'id': 2,
        'driver_id': '(dbid2,uuid2)',
        'merge_policy': 'append',
        'tags': ['reposition_offer_sent'],
        'created_at': datetime.datetime(2020, 5, 18, 12, 0, 0),
        'until': datetime.datetime(2020, 5, 18, 15, 0, 0),
    },
    {
        'id': 3,
        'driver_id': '(dbid3,uuid3)',
        'merge_policy': 'append',
        'tags': ['reposition_offer_sent'],
        'created_at': datetime.datetime(2020, 5, 18, 12, 0, 0),
        'until': datetime.datetime(2020, 5, 18, 15, 0, 0),
    },
    {
        'id': 4,
        'driver_id': '(dbid4,uuid4)',
        'merge_policy': 'append',
        'tags': ['reposition_offer_sent'],
        'created_at': datetime.datetime(2020, 5, 18, 11, 0, 0),
        'until': datetime.datetime(2020, 5, 18, 11, 30, 0),
    },
]


@pytest.mark.now('2020-05-18T12:00:00')
@pytest.mark.config(
    REPOSITION_RELOCATOR_TAGS_UPLOADER_ENABLED=True,
    REPOSITION_RELOCATOR_TAGS_UPLOADER_CONFIG={'processing_items_limit': 2},
)
@pytest.mark.pgsql('reposition-relocator', files=['data.sql'])
async def test_upload(taxi_reposition_relocator, pgsql, mockserver, testpoint):
    @testpoint('tags_uploader::end')
    def end(data):
        pass

    @mockserver.json_handler('/tags/v1/upload')
    def _mock_tags_upload(request):
        args = request.args
        assert args['provider_id'] == 'reposition-nirvana'

        data = json.loads(request.get_data())
        assert data == {
            'entity_type': 'dbid_uuid',
            'merge_policy': 'append',
            'tags': [
                {
                    'match': {
                        'id': 'dbid2_uuid2',
                        'until': '2020-05-18T15:00:00+0000',
                    },
                    'name': 'reposition_offer_sent',
                },
                {
                    'match': {
                        'id': 'dbid1_uuid1',
                        'until': '2020-05-18T15:00:00+0000',
                    },
                    'name': 'reposition_offer_sent',
                },
            ],
        }

        return mockserver.make_response('{}', status=200)

    def _get_tags_to_upload():
        return select_named(
            'SELECT * FROM state.uploading_tags',
            pgsql['reposition-relocator'],
        )

    assert _get_tags_to_upload() == INITIAL_TAGS

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'tags_uploader'},
    )
    assert response.status_code == 200

    await end.wait_call()
    assert _mock_tags_upload.times_called == 1

    changed_tags = INITIAL_TAGS[-2:]
    assert _get_tags_to_upload() == changed_tags


@pytest.mark.now('2020-05-18T12:00:00')
@pytest.mark.config(REPOSITION_RELOCATOR_TAGS_UPLOADER_ENABLED=True)
@pytest.mark.pgsql('reposition-relocator', files=['data.sql'])
async def test_cleaner(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @testpoint('tags_uploader-cleaner::end')
    def end(data):
        pass

    def _get_tags_to_upload():
        return select_named(
            'SELECT * FROM state.uploading_tags',
            pgsql['reposition-relocator'],
        )

    assert _get_tags_to_upload() == INITIAL_TAGS

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'tags_uploader-cleaner'},
    )
    assert response.status_code == 200

    await end.wait_call()

    changed_tags = INITIAL_TAGS[0:-1]
    assert _get_tags_to_upload() == changed_tags


@pytest.mark.config(REPOSITION_RELOCATOR_TAGS_UPLOADER_ENABLED=False)
@pytest.mark.pgsql('reposition-relocator', files=['data.sql'])
async def test_disabled(
        taxi_reposition_relocator, pgsql, mockserver, testpoint,
):
    @testpoint('tags_uploader::end')
    def end(data):
        pass

    @mockserver.json_handler('/tags/v1/upload')
    def _mock_tags_upload(request):
        args = request.args
        assert args['provider_id'] == 'reposition-nirvana'

        return mockserver.make_response('{}', status=200)

    def _get_tags_to_upload():
        return select_named(
            'SELECT * FROM state.uploading_tags',
            pgsql['reposition-relocator'],
        )

    assert _get_tags_to_upload() == INITIAL_TAGS

    response = await taxi_reposition_relocator.post(
        'service/cron', json={'task_name': 'tags_uploader'},
    )
    assert response.status_code == 200

    await end.wait_call()
    assert _mock_tags_upload.times_called == 0

    assert _get_tags_to_upload() == INITIAL_TAGS
