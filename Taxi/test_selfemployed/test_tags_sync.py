# pylint: disable=redefined-outer-name,unused-variable

import pytest

from selfemployed.generated.cron import run_cron


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, park_id, driver_id, status, step, created_at,
            modified_at)
        VALUES
            ('smz1', 'unbound_1', 'p1', 'd1', 'confirmed', 'requisites', NOW(),
            NOW()),
            ('smz2', 'unbound_2', 'p1', 'd2', 'confirmed', 'requisites', NOW(),
            NOW())
        """,
    ],
)
async def test_tags_sync(mock_token_update, patch, mockserver):
    @patch('taxi.clients.tags.TagsClient._request')
    async def request_tags_client(location, json, *args, **kwargs):
        match = [json['tags'][i]['match']['id'] for i in range(2)]
        if json['entity_type'] == 'park':
            assert match == ['p1', 'p1']
        elif json['entity_type'] == 'udid':
            assert match == ['udid1', 'udid2']
        else:
            assert False
        return {'status': 'ok'}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def get_udid(request):
        unique_drivers = {'p1_d1': 'udid1', 'p1_d2': 'udid2'}
        result = {'uniques': []}
        for profile_id in request.json['profile_id_in_set']:
            profile_result = {'park_driver_profile_id': profile_id, 'data': {}}
            unique_driver_id = unique_drivers.get(profile_id)
            if unique_driver_id:
                profile_result['data'] = {
                    'unique_driver_id': unique_drivers.get(profile_id),
                }
            result['uniques'].append(profile_result)
        return result

    await run_cron.main(['selfemployed.crontasks.tags_sync', '-t', '0'])

    assert len(request_tags_client.calls) == 3


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, park_id, driver_id, status, step, created_at,
            modified_at)
        VALUES
            ('smz1', 'unbound_1', 'p1', 'd1', 'confirmed', 'permission', NOW(),
            NOW())
        """,
    ],
)
async def test_tags_sync_without_requisites(
        mock_token_update, patch, mockserver,
):
    @patch('taxi.clients.tags.TagsClient._request')
    async def request_tags_client(location, json, *args, **kwargs):
        assert json['entity_type'] == 'park'
        assert json['tags'][0]['match']['id'] == 'p1'
        assert json['tags'][0]['name'] == 'selfemployed'
        return {'status': 'ok'}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def get_udid(request):
        return {'uniques': [{'park_driver_profile_id': 'p1_d1', 'data': {}}]}

    await run_cron.main(['selfemployed.crontasks.tags_sync', '-t', '0'])

    assert len(request_tags_client.calls) == 1
