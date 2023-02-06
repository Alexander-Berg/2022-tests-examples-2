import dataclasses
import datetime

import pytest

from crm_admin import entity
from crm_admin.generated.service.swagger import models
from crm_admin.storage import creative_adapters


def _serialize_creative_entity(creative: entity.Creative):
    serialized_creative = dataclasses.asdict(creative)
    serialized_creative['params'] = serialized_creative['params'].serialize()
    serialized_creative['created_at'] = serialized_creative[
        'created_at'
    ].strftime('%Y-%m-%d %H:%M:%S')
    if serialized_creative['updated_at'] is None:
        del serialized_creative['updated_at']
    else:
        serialized_creative['updated_at'] = serialized_creative[
            'updated_at'
        ].strftime('%Y-%m-%d %H:%M:%S')

    return serialized_creative


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch(web_context, load_json):
    db_creative = creative_adapters.DbCreative(web_context)

    creative_id = 1

    creative = _serialize_creative_entity(await db_creative.fetch(creative_id))

    expected = load_json('creatives.json')[str(creative_id)]

    assert creative == expected


@pytest.mark.now('2021-02-01T12:00:00')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update(web_context, load_json):
    db_creative = creative_adapters.DbCreative(web_context)

    expected = load_json('creatives.json')['update']

    await db_creative.update(
        entity.Creative(
            creative_id=expected['creative_id'],
            name=expected['name'],
            params=models.api.DriverSmsCreativeInfo.deserialize(
                expected['params'], allow_extra=True,
            ),
            extra_data=expected['extra_data'],
            created_at=datetime.datetime.strptime(
                expected['created_at'], '%Y-%m-%d %H:%M:%S',
            ),
            root_id=expected['root_id'],
            parent_id=expected['parent_id'],
            child_id=expected['child_id'],
            version_state=expected['version_state'],
        ),
    )

    creative = _serialize_creative_entity(
        await db_creative.fetch(expected['creative_id']),
    )

    assert creative == expected


@pytest.mark.now('2021-02-01T12:00:00')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update_params(web_context, load_json):
    db_creative = creative_adapters.DbCreative(web_context)

    expected = load_json('creatives.json')['update_params']

    await db_creative.update_params(
        creative_id=expected['creative_id'],
        params=models.api.DriverSmsCreativeInfo.deserialize(
            expected['params'], allow_extra=True,
        ),
    )

    creative = _serialize_creative_entity(
        await db_creative.fetch(expected['creative_id']),
    )

    assert creative == expected


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_approve(web_context):
    db_creative = creative_adapters.DbCreative(web_context)

    creative_id = 1

    await db_creative.approve(creative_id)

    creative = _serialize_creative_entity(await db_creative.fetch(creative_id))

    assert creative['approved']


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clear_by_campaign(web_context):
    campaign_id = 1
    creative_id = 1

    db_creative = creative_adapters.DbCreative(web_context)
    await db_creative.clear_by_campaign_id(campaign_id)

    with pytest.raises(entity.EntityNotFound):
        await db_creative.fetch(creative_id)
