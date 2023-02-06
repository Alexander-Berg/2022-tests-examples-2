import pytest

from crm_admin import settings
from crm_admin.storage import campaign_creative_connection_adapter


@pytest.mark.parametrize('json_id, result', [('create', 201), ('empty', 400)])
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_create_creative(
        web_context, web_app_client, load_json, json_id, result,
):
    expected_creatives = load_json('creatives.json')[json_id]
    campaign_id = 1

    for expected_creative in expected_creatives:
        response = await web_app_client.post(
            '/v1/creatives',
            json=expected_creative,
            params={'campaign_id': campaign_id},
        )

        assert response.status == result
        if response.status == 201:
            retrieved_creative = await response.json()

            assert (
                retrieved_creative['version_info']['version_state']
                == settings.VersionState.DRAFT
            )

            del expected_creative['version_info']['version_state']
            del retrieved_creative['version_info']['version_state']

            assert expected_creative == retrieved_creative

            db_connect = campaign_creative_connection_adapter.DbCreativeLink(
                web_context,
            )

            connect = await db_connect.fetch(
                connection_id=expected_creative['id'],
            )
            assert connect.creative_id == expected_creative['id']
            assert connect.campaign_id == campaign_id


@pytest.mark.parametrize(
    'json_id, result', [('create', 200), ('doesn\'t_exist_create', 404)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_read_creative(web_app_client, load_json, json_id, result):
    expected_creatives = load_json('creatives.json')[json_id]

    for expected_creative in expected_creatives:
        creative_id = expected_creative['id']
        response = await web_app_client.get(f'/v1/creatives/{creative_id}')

        assert response.status == result

        if response.status == 200:
            retrieved_creative = await response.json()
            assert expected_creative == retrieved_creative


@pytest.mark.parametrize(
    'json_id, result', [('update', 200), ('doesn\'t_exist_update', 404)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update_creative(web_app_client, load_json, json_id, result):
    exists_creatives = load_json('creatives.json')['create']
    update_creatives = load_json('creatives.json')[json_id]

    for (exists_creative, update_creative) in zip(
            exists_creatives, update_creatives,
    ):
        creative_id = update_creative['id']
        del update_creative['id']
        response = await web_app_client.put(
            f'/v1/creatives/{creative_id}', json=update_creative,
        )

        assert response.status == result

        if response.status == 200:
            retrieved_creative = await response.json()
            expected_creative = dict(exists_creative, **update_creative)
            assert expected_creative == retrieved_creative


@pytest.mark.parametrize(
    'campaign_id, limit, offset',
    [
        (1, None, None),
        (2, 1, None),
        (3, None, 1),
        (1, 1, 1),
        (None, 2, 2),
        (None, None, None),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_creative_campaigns.sql'])
async def test_get_creatives(
        web_app_client, load_json, campaign_id, limit, offset,
):
    creatives_json = load_json('creatives.json')
    expected_creatives = creatives_json['create']
    params = {}

    if campaign_id:
        params['campaign_id'] = campaign_id
        expected_creatives_id = creatives_json['campaigns'][str(campaign_id)]
    else:
        expected_creatives_id = creatives_json['campaigns']['null']
    if offset:
        params['offset'] = offset
        expected_creatives_id = expected_creatives_id[offset:]
    if limit:
        params['limit'] = limit
        expected_creatives_id = expected_creatives_id[:limit]

    response = await web_app_client.get('/v1/creatives', params=params)

    assert response.status == 200

    for pos, creative in enumerate(await response.json()):
        assert creative['id'] == expected_creatives_id[pos]
        assert creative == expected_creatives[creative['id'] - 1]


async def test_creatives_channels(web_app_client, load_json):
    expected_channels = load_json('creatives_channels.json')['channels']
    response = await web_app_client.get('/v1/channels')

    assert response.status == 200
    assert (await response.json()) == expected_channels


@pytest.mark.parametrize(
    'creative_id, expected_response', [(1, 400), (2, 200)],
)
@pytest.mark.pgsql('crm_admin', files=['init_creative_groups.sql'])
async def test_check_group_on_creative_update(
        web_app_client, creative_id, expected_response,
):
    update_creative = {
        'name': 'kek',
        'params': {
            'channel_name': 'driver_push',
            'code': 100,
            'content': 'Hello!',
        },
    }
    response = await web_app_client.put(
        f'/v1/creatives/{creative_id}', json=update_creative,
    )
    assert response.status == expected_response
