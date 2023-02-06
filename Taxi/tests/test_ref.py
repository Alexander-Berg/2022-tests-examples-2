import pytest

from swaggen import exceptions
from swaggen import ref as ref_module
from swaggen import schema as schema_mod
from swaggen import settings as settings_mod
from swaggen import tracing


@pytest.mark.parametrize(
    'definitions, ref, cycle',
    [
        (
            {
                'A': {'$ref': '#/definitions/B'},
                'B': {'$ref': '#/definitions/A'},
            },
            '#/definitions/A',
            ['#/definitions/B', '#/definitions/A'],
        ),
        (
            {
                'A': {'$ref': '#/definitions/B'},
                'B': {'$ref': '#/definitions/A'},
            },
            '#/definitions/B',
            ['#/definitions/A', '#/definitions/B'],
        ),
        (
            {'A': {'$ref': '#/definitions/A'}},
            '#/definitions/A',
            ['#/definitions/A'],
        ),
        (
            {
                'A': {'$ref': '#/definitions/B'},
                'B': {'$ref': '#/definitions/C'},
                'C': {'$ref': '#/definitions/D'},
                'D': {'$ref': '#/definitions/B'},
            },
            '#/definitions/A',
            ['#/definitions/C', '#/definitions/D', '#/definitions/B'],
        ),
        (
            {
                'A': {'$ref': '#/definitions/B'},
                'B': {'$ref': '#/definitions/C'},
                'C': {'$ref': '#/definitions/D'},
                'D': {'$ref': '#/definitions/B'},
            },
            '#/definitions/C',
            ['#/definitions/D', '#/definitions/B', '#/definitions/C'],
        ),
    ],
)
def test_cycle(definitions, ref, cycle):
    resolver = ref_module.Resolver(
        ref_module.TargetedSchema(
            schema=schema_mod.Schema(
                data=tracing.Dict(
                    {'definitions': definitions}, filepath='api.yaml',
                ),
                source=schema_mod.SchemaSource(
                    source_name='api',
                    source_type=schema_mod.SourceType.API,
                    target=settings_mod.ParsingTarget.SERVER,
                ),
            ),
            namespace='api',
            module='api',
            full_package='generated.swagger',
        ),
        {},
    )
    with pytest.raises(exceptions.SwaggenError) as exc_info:
        resolver.resolve_object(
            tracing.Dict({'$ref': ref}, filepath='api.yaml'),
        )

    assert exc_info.value.args == ('references cycle found', cycle)
