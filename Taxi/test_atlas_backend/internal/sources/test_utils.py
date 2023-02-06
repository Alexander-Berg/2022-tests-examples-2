import typing as tp

import pytest

from atlas_backend.internal.sources.models import utils


class TestNativeTypeGetter:
    @pytest.mark.parametrize(
        'db_type, native_type',
        [
            ('String', 'STR'),
            ('Int8', 'INT'),
            ('Int256', 'INT'),
            ('UInt8', 'INT'),
            ('UInt256', 'INT'),
        ],
    )
    def test_simple_type(self, db_type: str, native_type: str) -> None:
        assert utils.get_native_type_from_db_type(db_type) == native_type

    @pytest.mark.parametrize(
        'db_type, native_type',
        [
            ('Array(String)', 'ARRAY_OF_STR'),
            ('Array(Int8)', 'ARRAY_OF_INT'),
            ('Array(Int256)', 'ARRAY_OF_INT'),
            ('Array(UInt8)', 'ARRAY_OF_INT'),
            ('Array(UInt256)', 'ARRAY_OF_INT'),
            ('Nullable(String)', 'NULLABLE_STR'),
            ('Nullable(Int8)', 'NULLABLE_INT'),
            ('Nullable(Int256)', 'NULLABLE_INT'),
            ('Nullable(UInt8)', 'NULLABLE_INT'),
            ('Nullable(UInt256)', 'NULLABLE_INT'),
        ],
    )
    def test_complex_type(self, db_type: str, native_type: str) -> None:
        assert utils.get_native_type_from_db_type(db_type) == native_type

    @pytest.mark.parametrize(
        'db_type, native_type',
        [
            ('LowCardinality(Array(String))', 'ARRAY_OF_STR'),
            ('Array(LowCardinality(Int8))', 'ARRAY_OF_INT'),
            ('LowCardinality(Array(Int256))', 'ARRAY_OF_INT'),
            ('Array(LowCardinality(UInt8))', 'ARRAY_OF_INT'),
            ('LowCardinality(Array(UInt256))', 'ARRAY_OF_INT'),
            ('Nullable(LowCardinality(String))', 'NULLABLE_STR'),
            ('LowCardinality(Nullable(Int8))', 'NULLABLE_INT'),
            ('Nullable(LowCardinality(Int256))', 'NULLABLE_INT'),
            ('LowCardinality(Nullable(UInt8))', 'NULLABLE_INT'),
            ('Nullable(LowCardinality(UInt256))', 'NULLABLE_INT'),
        ],
    )
    def test_transparent_type(self, db_type: str, native_type: str) -> None:
        assert utils.get_native_type_from_db_type(db_type) == native_type

    @pytest.mark.parametrize(
        'db_type',
        [
            'Nullable(Array(String))',
            'Array(Nullable(Int8))',
            'Nullable(Nothing)',
            'NULL',
        ],
    )
    def test_unsupported_type(self, db_type: str) -> None:
        native_type = 'UNSUPPORTED_TYPE'
        assert utils.get_native_type_from_db_type(db_type) == native_type


class TestMetadataGetter:
    @pytest.mark.parametrize(
        'db_type, metadata',
        [
            (
                'LowCardinality',
                {'low_cardinality': {'value': True, 'set_by': ''}},
            ),
            ('DateTime(\'UTC\')', {'utc_offset': {'value': 0, 'set_by': ''}}),
            (
                'DateTime64(\'UTC\')',
                {'utc_offset': {'value': 0, 'set_by': ''}},
            ),
            (
                'LowCardinality(String)',
                {'low_cardinality': {'value': True, 'set_by': ''}},
            ),
        ],
    )
    def test_simple_type(
            self, db_type: str, metadata: tp.Dict[str, tp.Dict[str, tp.Any]],
    ) -> None:
        assert utils.get_metadata_from_db_type(db_type) == metadata

    @pytest.mark.parametrize(
        'db_type, metadata',
        [
            (
                'LowCardinality(DateTime(\'UTC\'))',
                {
                    'low_cardinality': {'value': True, 'set_by': ''},
                    'utc_offset': {'value': 0, 'set_by': ''},
                },
            ),
            (
                'LowCardinality(DateTime64(\'UTC\'))',
                {
                    'low_cardinality': {'value': True, 'set_by': ''},
                    'utc_offset': {'value': 0, 'set_by': ''},
                },
            ),
        ],
    )
    def test_complex_type(
            self, db_type: str, metadata: tp.Dict[str, tp.Dict[str, tp.Any]],
    ) -> None:
        assert utils.get_metadata_from_db_type(db_type) == metadata

    @pytest.mark.parametrize(
        'db_type',
        [
            'String',
            'Int8',
            'Int256',
            'UInt8',
            'UInt256',
            'Nullable(String)',
            'Nullable(Int8)',
            'Nullable(Int256)',
            'Nullable(UInt8)',
            'Nullable(UInt256)',
        ],
    )
    def test_unsupported_type(self, db_type: str) -> None:
        assert not utils.get_metadata_from_db_type(db_type)


class TestUsedColumnsGetter:
    @pytest.mark.parametrize(
        'expression, columns',
        [
            ('foo {lol} bar', ['lol']),
            ('{lol} {{}} {kek} __', ['lol', 'kek']),
            ('{foo_bar} bar_foo', ['foo_bar']),
        ],
    )
    def used_columns(self, expression: str, columns: tp.List[str]) -> None:
        assert utils.get_used_columns(expression) == columns

    @pytest.mark.parametrize('expression', ['{{lol}} !!!', 'foo}}bar{{kek'])
    def no_columns(self, expression: str) -> None:
        assert not utils.get_used_columns(expression)
