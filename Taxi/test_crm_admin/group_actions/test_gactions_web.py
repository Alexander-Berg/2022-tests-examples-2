import typing

import pytest

from crm_admin import storage
from crm_admin.generated.service.swagger import models
from crm_admin.group_action import group_action
from crm_admin.group_action.details import creative_details
from crm_admin.group_action.details import details_mapping

OWNER_OF_ALL = 'test_owner'


def build_entity_gaction(
        parent_id: typing.Optional[int] = None,
) -> group_action.GroupAction:
    result = group_action.GroupAction(
        gaction_id=1,
        group_id=1,
        parent_id=parent_id,
        type=details_mapping.DetailsType.CREATIVE,
        details=creative_details.CreativeDetails(creative_id=1),
        version_info=group_action.VersionInfo.blank(),
    )
    return result


def build_api_gaction(
        id_: typing.Optional[int] = None,
        parent_id: typing.Optional[int] = None,
        mutator_params: typing.Optional[
            models.api.GroupActionMutatorParams
        ] = None,
) -> models.api.GroupAction:
    result = models.api.GroupAction(
        id=id_,
        group_action_type=str(details_mapping.DetailsType.CREATIVE),
        group_id=1,
        item_id=1,
        parent_id=parent_id,
        extra_data=models.api.GroupActionExtraData(
            mutator_params=mutator_params,
        ),
    )
    return result


def compare_by_keys(expected: dict, got: dict):
    for key, expected_val in expected.items():
        got_val = got[key]
        if isinstance(expected_val, dict):
            compare_by_keys(expected=expected_val, got=got_val)
        else:
            assert expected_val == got_val, key


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_create_gaction(web_context, web_app_client):
    # create first gaction in a group
    gaction_body = build_api_gaction()
    response = await web_app_client.post(
        '/v1/group_actions',
        json=gaction_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200

    expected = gaction_body.serialize()
    got = await response.json()
    compare_by_keys(expected=expected, got=got)

    # create second gaction in a group - should have parent id link
    gaction_body = build_api_gaction(parent_id=1)
    response = await web_app_client.post(
        '/v1/group_actions',
        json=gaction_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200

    expected = gaction_body.serialize()
    got = await response.json()
    compare_by_keys(expected=expected, got=got)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update_gaction(web_context, web_app_client):
    db_gaction = storage.DbGroupAction(context=web_context)
    await db_gaction.create(gaction=build_entity_gaction())

    # create first gaction in a group
    gaction_body = build_api_gaction(
        id_=1,
        mutator_params=models.api.GroupActionMutatorParams(
            deeplink_from_context_gaid=None,
        ),
    )
    response = await web_app_client.put(
        '/v1/group_actions',
        json=gaction_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200

    expected = gaction_body.serialize()
    got = await response.json()
    compare_by_keys(expected=expected, got=got)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_delete_gaction(web_context, web_app_client):
    db_gaction = storage.DbGroupAction(context=web_context)
    await db_gaction.create(gaction=build_entity_gaction())

    group_id = 1
    gaction_id = 1
    response = await web_app_client.delete(
        f'/v1/group_actions?group_id={group_id}&group_action_id={gaction_id}',
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_gaction(web_context, web_app_client):
    db_gaction = storage.DbGroupAction(context=web_context)
    await db_gaction.create(gaction=build_entity_gaction())

    gaction_id = 1
    response = await web_app_client.get(
        f'/v1/group_actions?group_action_id={gaction_id}',
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200

    gaction_model = build_api_gaction()
    expected = gaction_model.serialize()
    got = await response.json()
    compare_by_keys(expected=expected, got=got)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_gaction_list(web_context, web_app_client):
    db_gaction = storage.DbGroupAction(context=web_context)
    await db_gaction.create(gaction=build_entity_gaction())
    await db_gaction.create(gaction=build_entity_gaction(parent_id=1))

    group_id = 1
    response = await web_app_client.get(
        f'/v1/group_actions/list?group_id={group_id}',
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200

    got = await response.json()
    expected_len = 2
    assert expected_len == len(got)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_missing_gaction(web_context, web_app_client):
    gaction_id = 1
    response = await web_app_client.get(
        f'/v1/group_actions?group_action_id={gaction_id}',
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 400
    got = await response.json()
    expected = {'message': 'Group Action id=1 was not found'}
    assert expected == got


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_gactions_validation(web_context, web_app_client):
    db_gaction = storage.DbGroupAction(context=web_context)
    await db_gaction.create(gaction=build_entity_gaction())
    await db_gaction.create(gaction=build_entity_gaction(parent_id=1))

    # creating more than one gaction without link to parent should fail
    gaction_body = build_api_gaction()
    response = await web_app_client.post(
        '/v1/group_actions',
        json=gaction_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 400

    got = await response.json()
    expected = {
        'errors': [
            {
                'code': 'group_action_invalid_links',
                'details': {
                    'reason': (
                        'Unable to build valid'
                        ' supported graph with provided links'
                    ),
                },
            },
        ],
    }

    assert expected == got

    # creating gaction with link to non-existent parent should fail
    gaction_body = build_api_gaction(parent_id=100500)
    response = await web_app_client.post(
        '/v1/group_actions',
        json=gaction_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 400
    assert expected == got

    # deleting parent gaction should fail
    group_id = 1
    gaction_id = 1
    response = await web_app_client.delete(
        f'/v1/group_actions?group_id={group_id}&group_action_id={gaction_id}',
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 400
    assert expected == got
