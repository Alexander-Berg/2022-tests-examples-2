# pylint: disable=import-only-modules
import json

import pytest

from .utils import select_named


@pytest.mark.config(
    REPOSITION_API_TAGS_UPLOADER_CONFIG={
        'enabled': False,
        'processing_items_limit': 1,
        'parallel_provider_processing_limit': 1,
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'many_uploading_tags.sql'],
)
async def test_disabled(taxi_reposition_api, mockserver):
    @mockserver.json_handler('/tags/v1/upload')
    def mock_upload(request):
        return {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'tags-uploader'},
        )
    ).status_code == 200

    assert mock_upload.times_called == 0


@pytest.mark.now('2019-09-01T12:00:09')
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'many_uploading_tags.sql'],
)
@pytest.mark.parametrize('tags_request_failed', [False, True])
@pytest.mark.now('2019-09-01T12:00:10')
@pytest.mark.config(
    REPOSITION_API_TAGS_UPLOADER_CONFIG={
        'enabled': True,
        'processing_items_limit': 1000,
        'parallel_provider_processing_limit': 100,
    },
)
async def test_upload(
        taxi_reposition_api, pgsql, mockserver, load_json, tags_request_failed,
):
    rows = select_named(
        """
        SELECT provider, tags_id, CONCAT((driver_id).dbid,'_',(driver_id).uuid)
        driver_id, merge_policy, tags, ttl
        FROM state.uploading_tags
        INNER JOIN settings.driver_ids
        ON uploading_tags.driver_id_id = driver_ids.driver_id_id
        WHERE ttl >= '2019-09-01T12:00:09' AND uploaded = FALSE
        ORDER BY tags_id
        """,
        pgsql['reposition'],
    )
    already_uploaded_rows = select_named(
        """
        SELECT provider, COUNT(tags_id)
        FROM state.uploading_tags WHERE NOT uploaded GROUP BY provider
        """,
        pgsql['reposition'],
    )

    tags_calls_by_providers = {}
    tags_upload_queue_by_driver_ids = {}
    for row in rows:
        provider = row['provider']
        driver_id = row['driver_id']
        merge_policy = row['merge_policy']

        if provider not in tags_upload_queue_by_driver_ids:
            tags_upload_queue_by_driver_ids[provider] = {}

        if driver_id not in tags_upload_queue_by_driver_ids[provider]:
            tags_upload_queue_by_driver_ids[provider][driver_id] = []

        tags_upload_queue_by_driver_ids[provider][driver_id].append(
            {'merge_policy': merge_policy, 'tags': list(row['tags'])},
        )

    @mockserver.json_handler('/tags/v1/upload')
    def mock_upload(request):
        args = request.args
        provider = args['provider_id']

        if provider not in tags_calls_by_providers:
            tags_calls_by_providers[provider] = 0

        tags_calls_by_providers[provider] += 1

        data = json.loads(request.get_data())

        if tags_request_failed and tags_calls_by_providers[provider] > 1:
            return mockserver.make_response('Bad Request', status=400)

        assert data['entity_type'] == 'dbid_uuid'

        merge_policy = data['merge_policy']
        tags = data['tags']

        provider_queue = tags_upload_queue_by_driver_ids[provider]

        for tag in tags:
            tag_name = tag['name']
            driver_id = tag['match']['id']
            driver_queue = provider_queue[driver_id]

            assert merge_policy == driver_queue[0]['merge_policy']
            assert tag_name in driver_queue[0]['tags']

            driver_queue[0]['tags'].remove(tag_name)

            if not driver_queue[0]['tags']:
                del driver_queue[0]
            if not driver_queue:
                del provider_queue[driver_id]

        if not provider_queue:
            del tags_upload_queue_by_driver_ids[provider]

        return {}

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'tags-uploader'},
        )
    ).status_code == 200

    rows = select_named(
        """
        SELECT provider, COUNT(tags_id)
        FROM state.uploading_tags
        WHERE NOT uploaded AND ttl >= '2019-09-01T12:00:09'
        GROUP BY provider
        """,
        pgsql['reposition'],
    )

    if not tags_request_failed:
        assert mock_upload.times_called == 7
        assert not tags_upload_queue_by_driver_ids
        assert not rows
    else:
        assert mock_upload.times_called == 4
        # assert that at least one bulk was uploaded for each provider
        for row in rows:
            for up_row in already_uploaded_rows:
                if row['provider'] == up_row['provider']:
                    assert row['count'] < up_row['count']


@pytest.mark.now('2019-09-01T12:00:10')
@pytest.mark.config(
    REPOSITION_API_TAGS_UPLOADER_CONFIG={
        'enabled': True,
        'processing_items_limit': 1,
        'parallel_provider_processing_limit': 1,
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'many_uploading_tags.sql'],
)
async def test_limit(taxi_reposition_api, pgsql, mockserver):
    @mockserver.json_handler('/tags/v1/upload')
    def mock_upload(request):
        return {}

    already_uploaded_rows = select_named(
        """
        SELECT COUNT(tags_id) FROM state.uploading_tags WHERE NOT uploaded
        """,
        pgsql['reposition'],
    )

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': 'tags-uploader'},
        )
    ).status_code == 200

    assert mock_upload.times_called == 1

    uploaded_rows = select_named(
        """
        SELECT COUNT(tags_id) FROM state.uploading_tags WHERE NOT uploaded
        """,
        pgsql['reposition'],
    )

    assert already_uploaded_rows[0]['count'] - uploaded_rows[0]['count'] == 1
