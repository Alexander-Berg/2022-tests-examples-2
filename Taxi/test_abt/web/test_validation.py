import pytest

from abt.generated.service.swagger.models import api as api_models
from abt.logic import validation
from test_abt.helpers import builders as builders_module


BUILDERS = builders_module.Builders()


@pytest.mark.parametrize(
    ['config', 'facets_config', 'expected_error_code'],
    [
        pytest.param(
            'bad config',
            {},
            validation.ErrorCode.ConfigParseError,
            id='Some bad string',
        ),
        pytest.param(
            '',
            {},
            validation.ErrorCode.ConfigParseError,
            id='valid yaml and invalid config',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric()
            .add_precomputes()
            .add_observations(
                args=[{'arg': 'unsupported_arg', 'column': 'phoneid'}],
            )
            .build_yaml(),
            {},
            validation.ErrorCode.ConfigParseError,
            id='invalid observations args',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric()
            .add_precomputes(
                facets=BUILDERS.get_facets_builder()
                .add_custom_facet('ios', ['ios'])
                .build(),
            )
            .build_yaml(),
            {},
            validation.ErrorCode.NotDeclaredFacets,
            id='facet not declared in ABT_FACETS_V2',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric()
            .add_precomputes(
                facets=BUILDERS.get_facets_builder()
                .add_custom_facet('ios', ['ios', 'moscow'])
                .build(),
            )
            .build_yaml(),
            {'ios': {'description': 'hello', 'title_key': 'hello'}},
            validation.ErrorCode.FieldsAggRequired,
            id='facet has 2 fields but no agg function',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric(name='abra')
            .add_value_metric(name='abra')
            .add_precomputes()
            .build_yaml(),
            {},
            validation.ErrorCode.DuplicatedMetricsNames,
            id='duplicated metrics names',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric(name='a')
            .add_precomputes()
            .build_yaml(),
            {},
            validation.ErrorCode.InvalidMetricName,
            id='short metric name',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric()
            .add_precomputes()
            .build_yaml(),
            {},
            None,
            id='OK',
        ),
        pytest.param(
            BUILDERS.get_mg_config_builder()
            .add_value_metric(name='TRATATA89')
            .add_precomputes()
            .build_yaml(),
            {},
            None,
            id='OK with uppercase',
        ),
    ],
)
async def test_metrics_groups_config_syntax_validator(
        config, facets_config, expected_error_code,
):
    validator = validation.MetricsGroupsConfigSyntaxValidator(
        config, facets_config,
    )

    if expected_error_code is not None:
        with pytest.raises(validation.ValidationError) as excinfo:
            await validator.validate()
        assert excinfo.value.code == expected_error_code.value
    else:
        assert isinstance(
            await validator.validate(), api_models.MetricsGroupConfig,
        )


@pytest.mark.parametrize(
    ['existing_scopes', 'scopes_to_check', 'expected_error_code'],
    [
        pytest.param(
            [{'scope': 'some_scope', 'description': 'dummy'}],
            ['some_another_scope'],
            validation.ErrorCode.AbsentScopes,
            id='absent scopes',
        ),
        pytest.param(
            [{'scope': 'some_scope', 'description': 'dummy'}],
            ['some_scope'],
            None,
            id='OK',
        ),
    ],
)
async def test_metrics_groups_scopes_validator(
        existing_scopes, scopes_to_check, expected_error_code,
):
    validator = validation.MetricsGroupsScopesValidator(
        existing_scopes, scopes_to_check,
    )

    if expected_error_code is not None:
        with pytest.raises(validation.ValidationError) as excinfo:
            await validator.validate()
        assert excinfo.value.code == expected_error_code.value
    else:
        assert (await validator.validate()) is None


@pytest.mark.parametrize(
    ['left', 'right', 'expected_error_code'],
    [
        pytest.param(10, 11, validation.ErrorCode.Conflict, id='!='),
        pytest.param(10, 10, None, id='=='),
    ],
)
async def test_equality_validator(left, right, expected_error_code):
    validator = validation.EqualityValidator(
        left, right, validation.ErrorCode.Conflict, 'some msg',
    )

    if expected_error_code is not None:
        with pytest.raises(validation.ValidationError) as excinfo:
            await validator.validate()
        assert excinfo.value.code == expected_error_code.value
    else:
        assert (await validator.validate()) is None
