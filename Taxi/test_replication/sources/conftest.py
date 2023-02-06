import datetime
import functools
import os

import pytest

from replication import settings
from replication.foundation import consts
from replication.foundation import loaders
from replication.foundation.sources import constructor as source_constructor


@pytest.fixture
def source_meta_checker(replication_ctx):
    return functools.partial(_source_meta_checker, replication_ctx)


def _source_meta_checker(
        replication_ctx,
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
):
    raw_meta = raw_meta.copy()
    raw_meta.setdefault('type', source_type)
    builder = loaders.SourceCoreBuilder(
        replication_ctx.pluggy_deps.source_definitions,
        '',
        source_name,
        consts.ReplicationType.QUEUE,
        raw_meta,
    )
    if source_type == consts.SOURCE_TYPE_QUEUE_MONGO:
        queue_data = raw_meta.get('queue_data')
        source_core = builder.load_source_core(queue_data=queue_data)
    else:
        source_core = builder.load_source_core()
    sources = source_constructor.construct(
        source_core, rule_keeper=replication_ctx.rule_keeper,
    )
    assert len(sources) == len(expected_names)

    for num, (source, expected_name) in enumerate(
            zip(sources, expected_names),
    ):
        assert source.type == source_type
        assert source.name == expected_name
        if expected_meta_attrs is None:
            continue

        assert source.base_meta.replicate_by
        assert source.base_meta.data_chunk_size == (
            settings.DEFAULT_DATA_CHUNK_SIZE
        )
        assert source.base_meta.time_chunk_size == (
            datetime.timedelta(seconds=300)
        )
        for attribute, expected_values in expected_meta_attrs.items():
            attrs = attribute.split('.')
            meta = source.meta
            if attrs[0] in ('unit_name', 'iteration_type', 'replicate_by'):
                meta = source.base_meta
            attr_value = getattr(meta, attrs[0])
            for attr in attrs[1:]:
                attr_value = attr_value[attr]
            expected = expected_values[num]
            assert attr_value == expected


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'source#' + os.path.basename(os.path.dirname(static_dir))
