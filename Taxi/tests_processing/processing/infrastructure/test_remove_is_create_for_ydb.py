import dataclasses
from typing import Any
from typing import Dict
from typing import Optional

import pytest


@pytest.mark.processing_queue_config(
    'no-is-create.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.experiments3(filename='use_ydb.json')
async def test_remove_is_create_for_ydb(processing):
    item_id = '123456789'
    queue = processing.testsuite.foo
    event_id = await queue.send_event(item_id, payload={'kind': 'regular'})
    assert event_id


@pytest.mark.processing_queue_config(
    'no-is-create.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.config(PROCESSING_FORCE_YDB=True)
async def test_remove_is_create_for_ydb_recipe(processing):
    item_id = '123456789'
    queue = processing.testsuite.foo
    event_id = await queue.send_event(item_id, payload={'kind': 'regular'})
    assert event_id


@dataclasses.dataclass
class ProcessingEntityConfig:
    module: str
    scope: str
    queue: Optional[str] = None
    single_pipeline: Optional[str] = None
    main_operator: str = 'main'
    config_vars: Dict[str, Any] = dataclasses.field(default_factory=dict)


async def test_remove_is_create_for_pg(processing):
    with pytest.raises(AssertionError):
        await processing.load_fs_configs(
            [
                ProcessingEntityConfig(
                    module='no-is-create.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main',
                    config_vars={},
                ),
            ],
        )
    await processing.load_fs_configs([])


@pytest.mark.processing_queue_config(
    'ydb-is-create.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.experiments3(filename='use_ydb.json')
async def test_keep_is_create_for_ydb(processing, testpoint):
    @testpoint('ProcessingNgQueue::IsCreate')
    def is_create_tp(data):
        assert data['is_create'] is None

    item_id = '123456789'
    queue = processing.testsuite.foo
    event_id = await queue.send_event(item_id, payload={'kind': 'create'})
    assert event_id
    assert is_create_tp.times_called == 1


@pytest.mark.processing_queue_config(
    'ydb-is-create.yaml', scope='testsuite', queue='foo',
)
async def test_keep_is_create_for_pg(processing, testpoint):
    @testpoint('ProcessingNgQueue::IsCreate')
    def is_create_tp(data):
        assert data['is_create']

    item_id = '123456789'
    queue = processing.testsuite.foo
    event_id = await queue.send_event(item_id, payload={'kind': 'create'})
    assert event_id
    assert is_create_tp.times_called == 1
