import pytest

from taxi.codegen import swaggen_serialization

from startrack_reports.db import queries
from startrack_reports.generated.service.swagger.models import api

DEFAULT_LIMIT = 50


async def test_insert(web_context):
    inserted_rows = [
        api.Representation(
            action='drafts.commissions_create',
            data_key='zone',
            data_key_tanker_key='Зона',
            data_value_representation_function=None,
            position=1,
        ),
        api.Representation(
            action='drafts.commissions_create',
            data_key='enabled',
            data_key_tanker_key='Включена',
            data_value_representation_function='bool_repr',
            position=2,
        ),
        api.Representation(
            action='drafts.promocodes_edit',
            data_key='zone',
            data_key_tanker_key='Зона',
            data_value_representation_function=None,
            position=1,
        ),
    ]
    await queries.insert_representations(web_context, inserted_rows)

    rows = await queries.list_representations(web_context, None, DEFAULT_LIMIT)
    assert len(rows) == len(inserted_rows)

    with pytest.raises(queries.InsertError):
        await queries.insert_representations(web_context, inserted_rows)


@pytest.mark.pgsql('startrack_reports', files=['startrack_reports.sql'])
async def test_update(web_context):
    # check empty table
    result = await queries.update_representation(
        web_context,
        'drafts.commissions_edit',
        'zone',
        'Зона',
        'bool_repr',
        None,
    )
    assert len(result) == 1
    assert result[0]['data_value_representation_function'] == 'bool_repr'
    assert result[0]['position'] == 1

    result = await queries.update_representation(
        web_context, 'not_found', 'not_found', 'not_found', 'not_found', None,
    )
    assert result == []


@pytest.mark.pgsql('startrack_reports', files=['startrack_reports.sql'])
async def test_delete(web_context):
    result = await queries.delete_representation(
        web_context, 'drafts.commissions_create', 'enabled',
    )
    assert result

    result = await queries.delete_representation(
        web_context, 'drafts.commissions_create', 'enabled',
    )
    assert result == []


@pytest.mark.pgsql('startrack_reports', files=['startrack_reports.sql'])
async def test_list(web_context):
    action_rows = await queries.list_representations(
        web_context, 'drafts.commissions_create', None,
    )
    action_rows_with_ignored_limit = await queries.list_representations(
        web_context, 'drafts.commissions_create', 1,
    )
    # check correct filter by action (exclude limit)
    assert len(action_rows) > 1
    assert len(action_rows_with_ignored_limit) == len(action_rows)

    with pytest.raises(swaggen_serialization.ValidationError):
        # check validation
        await queries.list_representations(web_context, None, None)

    empty = await queries.list_representations(web_context, 'not_found', None)
    assert empty == []


@pytest.mark.pgsql('startrack_reports', files=['startrack_reports.sql'])
async def test_list_request(web_app_client):
    resp = await web_app_client.get(
        '/v1/representations/', params={'action': 'drafts.commissions_create'},
    )
    assert resp.status == 200
    action_rows = await resp.json()
    resp = await web_app_client.get(
        '/v1/representations/',
        params={'action': 'drafts.commissions_create', 'limit': '1'},
    )
    assert resp.status == 200
    action_rows_with_ignored_limit = await resp.json()
    # check correct filter by action (exclude limit)
    assert len(action_rows['items']) > 1
    assert len(action_rows_with_ignored_limit['items']) == len(
        action_rows['items'],
    )
