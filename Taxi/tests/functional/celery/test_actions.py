import datetime

import pytest
import freezegun

from taxi.robowarehouse.lib.concepts import celery as celery_concepts
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all():
    task1 = await celery_concepts.factories.create()
    task2 = await celery_concepts.factories.create()

    result = await celery_concepts.get_all()

    assert_items_equal([r.to_dict() for r in result], [
                       task1.to_dict(), task2.to_dict()])


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_status_count_by_delta_not_found():
    await celery_concepts.factories.create()

    delta = datetime.timedelta(minutes=10)
    result = await celery_concepts.get_status_count_by_delta(delta)

    assert result == {}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_status_count_by_delta():
    await celery_concepts.factories.create(status=celery_concepts.types.CeleryStatusType.SUCCESS,
                                                   date_done=datetime.datetime.utcnow())
    await celery_concepts.factories.create(status=celery_concepts.types.CeleryStatusType.SUCCESS,
                                                   date_done=datetime.datetime.utcnow())
    await celery_concepts.factories.create(status=celery_concepts.types.CeleryStatusType.FAILURE,
                                                   date_done=datetime.datetime.utcnow())

    delta = datetime.timedelta(minutes=10)

    expected = {'success': 2, 'failure': 1}
    result = await celery_concepts.get_status_count_by_delta(delta)

    assert result == expected
