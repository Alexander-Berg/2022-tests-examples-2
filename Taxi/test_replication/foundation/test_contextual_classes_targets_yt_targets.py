# pylint: disable=protected-access
import typing

import pytest

from replication.targets.yt import yt_targets


DEFAULT_INIT_KWARGS = {
    'description': 'description',
    'optimize_for': 'lookup',
    'primary_medium': 'ssd_blobs',
    'compression_codec': 'brotli_8',
    'erasure_codec': 'lrc_12_2_2',
}


class TableMetaTestCase(typing.NamedTuple):
    method: str
    expected: typing.Any
    kwargs: typing.Optional[dict] = None


@pytest.mark.parametrize(
    'init_kwargs,test_cases',
    [
        (
            {
                'schema': [
                    {
                        'name': 'col_1',
                        'type': 'string',
                        'sort_order': 'ascending',
                        'description': 'col_1 info',
                    },
                    {
                        'name': 'col_2',
                        'type': 'string',
                        'sort_order': 'ascending',
                        'description': 'col_2 info',
                    },
                    {
                        'name': 'col_3',
                        'type': 'int64',
                        'description': 'col_3 info',
                    },
                ],
            },
            [
                TableMetaTestCase('get_key_columns', ['col_1', 'col_2']),
                TableMetaTestCase(
                    'get_yt_schema',
                    [
                        {'name': 'col_1', 'type': 'string'},
                        {'name': 'col_2', 'type': 'string'},
                        {'name': 'col_3', 'type': 'int64'},
                    ],
                    {'no_sort': True},
                ),
                TableMetaTestCase(
                    'get_yt_yson_schema',
                    [
                        {
                            'name': 'col_1',
                            'type': 'string',
                            'sort_order': 'ascending',
                        },
                        {
                            'name': 'col_2',
                            'type': 'string',
                            'sort_order': 'ascending',
                        },
                        {'name': 'col_3', 'type': 'int64'},
                    ],
                    {'exclude_expression': True},
                ),
                TableMetaTestCase('get_description', 'description'),
                TableMetaTestCase(
                    'get_attributes',
                    {
                        'dynamic': True,
                        'optimize_for': 'lookup',
                        'primary_medium': 'ssd_blobs',
                        'compression_codec': 'brotli_8',
                        'erasure_codec': 'lrc_12_2_2',
                        'schema': [
                            {
                                'name': 'col_1',
                                'type': 'string',
                                'sort_order': 'ascending',
                            },
                            {
                                'name': 'col_2',
                                'type': 'string',
                                'sort_order': 'ascending',
                            },
                            {'name': 'col_3', 'type': 'int64'},
                        ],
                    },
                ),
            ],
        ),
        (
            {
                'enable_dynamic_store_read': True,
                'schema': [
                    {
                        'name': 'col_1',
                        'type': 'string',
                        'sort_order': 'ascending',
                        'description': 'col_1 info',
                    },
                ],
            },
            [
                TableMetaTestCase(
                    'get_attributes',
                    {
                        'dynamic': True,
                        'enable_dynamic_store_read': True,
                        'optimize_for': 'lookup',
                        'primary_medium': 'ssd_blobs',
                        'compression_codec': 'brotli_8',
                        'erasure_codec': 'lrc_12_2_2',
                        'schema': [
                            {
                                'name': 'col_1',
                                'type': 'string',
                                'sort_order': 'ascending',
                            },
                        ],
                    },
                ),
            ],
        ),
        (
            {
                'enable_dynamic_store_read': False,
                'schema': [
                    {
                        'name': 'col_1',
                        'type': 'string',
                        'sort_order': 'ascending',
                        'description': 'col_1 info',
                    },
                ],
            },
            [
                TableMetaTestCase(
                    'get_attributes',
                    {
                        'dynamic': True,
                        'enable_dynamic_store_read': False,
                        'optimize_for': 'lookup',
                        'primary_medium': 'ssd_blobs',
                        'compression_codec': 'brotli_8',
                        'erasure_codec': 'lrc_12_2_2',
                        'schema': [
                            {
                                'name': 'col_1',
                                'type': 'string',
                                'sort_order': 'ascending',
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
def test_table_meta(init_kwargs, test_cases, monkeypatch):
    old_yt_get_schema = yt_targets.TableMeta.get_yt_yson_schema
    monkeypatch.setattr(
        yt_targets.TableMeta,
        'get_yt_yson_schema',
        lambda self, **kwargs: list(old_yt_get_schema(self, **kwargs)),
    )

    init_kwargs = init_kwargs.copy()
    for key, value in DEFAULT_INIT_KWARGS.items():
        if key not in init_kwargs:
            init_kwargs[key] = value
    table_meta = yt_targets.TableMeta(**init_kwargs)
    for test_case in test_cases:
        result = getattr(table_meta, test_case.method)(
            **(test_case.kwargs or {}),
        )
        assert (
            result == test_case.expected
        ), f'Test case {test_case.method} failed'
