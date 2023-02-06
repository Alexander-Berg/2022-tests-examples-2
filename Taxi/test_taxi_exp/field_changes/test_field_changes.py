import pytest

from taxi_exp.generated.service.swagger.models.api import common as api
from taxi_exp.lib import biz_revision
from taxi_exp.lib import status_wait_prestable
from test_taxi_exp.helpers import experiment


WAIT_ON_PRESTABLE = 0


@pytest.mark.parametrize(
    'current_dict,new_model,significant_for_biz_revision,'
    'significant_for_wait_prestable',
    [
        pytest.param(
            experiment.generate(trait_tags=[]),
            experiment.generate(
                trait_tags=['analytical'],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            False,
            id='add analytical trait tag',
        ),
        pytest.param(
            experiment.generate(
                match_predicate=experiment.inset_predicate([1]),
            ),
            experiment.generate(
                match_predicate=experiment.DEFAULT_PREDICATE,
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='predicate in match',
        ),
        pytest.param(
            experiment.generate(
                action_time={
                    'from': '2020-01-01T00:00:00+03:00',
                    'to': '2021-12-31T23:59:59+03:00',
                },
            ),
            experiment.generate(
                action_time={
                    'from': '2020-01-01T00:00:00+03:00',
                    'to': '2023-12-31T23:59:59+03:00',
                },
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            False,
            id='action time',
        ),
        pytest.param(
            experiment.generate(consumers=[{'name': 'launch'}]),
            experiment.generate(
                consumers=[{'name': 'client_protocol/launch'}],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            False,
            id='consumers list',
        ),
        pytest.param(
            experiment.generate(default_value={}),
            experiment.generate(
                default_value={'enabled': True},
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='default value',
        ),
        pytest.param(
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': None}},
                ],
            ),
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            False,
            id='application',
        ),
        pytest.param(
            experiment.generate(
                action_time={
                    'from': '2020-01-01T00:00:00+03:00',
                    'to': '2021-12-31T23:59:59+03:00',
                },
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[experiment.make_clause('title')],
            ),
            experiment.generate(
                action_time={
                    'from': '2020-01-01T00:00:00+03:00',
                    'to': '2021-12-31T23:59:59+03:00',
                },
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='remove clause',
        ),
        pytest.param(
            experiment.generate(
                action_time={
                    'from': '2020-01-01T00:00:00+03:00',
                    'to': '2021-12-31T23:59:59+03:00',
                },
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[experiment.make_clause('title', alias='a1')],
            ),
            experiment.generate(
                action_time={
                    'from': '2020-01-01T00:00:00+03:00',
                    'to': '2021-12-31T23:59:59+03:00',
                },
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title', alias='a1', is_tech_group=True,
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            False,
            id='type clause to technical',
        ),
        pytest.param(
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title',
                        alias='a1',
                        predicate=experiment.DEFAULT_PREDICATE,
                    ),
                ],
            ),
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title',
                        alias='a1',
                        predicate=experiment.inset_predicate([1]),
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='predicate in clause',
        ),
        pytest.param(
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause('title', alias='a1', value={}),
                ],
            ),
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title', alias='a1', value={'enabled': True},
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='clause value',
        ),
        pytest.param(
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title',
                        alias='a1',
                        value={},
                        extended_value={'enabled': True},
                        extension_method='deep_extend',
                    ),
                ],
            ),
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title',
                        alias='a1',
                        value={},
                        extended_value={'enabled': False},
                        extension_method='deep_extend',
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='clause extended value',
        ),
        pytest.param(
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title',
                        alias='a1',
                        value={},
                        extended_value={'enabled': True},
                        extension_method='deep_extend',
                    ),
                ],
            ),
            experiment.generate(
                applications=[
                    {'name': 'ios', 'version_range': {'from': '1.0.0'}},
                ],
                clauses=[
                    experiment.make_clause(
                        'title',
                        alias='a1',
                        value={},
                        extended_value={'enabled': True},
                        extension_method='replace',
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            True,
            True,
            id='clause extension method',
        ),
        pytest.param(
            experiment.generate(),
            experiment.generate(
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            False,
            id='no changed experiment',
        ),
        pytest.param(
            experiment.generate(st_tickets=[]),
            experiment.generate(
                st_tickets=['TAXIEXP-123'],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            False,
            id='st_ticket',
        ),
        pytest.param(
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'tech_clause',
                        is_tech_group=True,
                        predicate={'type': 'true'},
                    ),
                ],
            ),
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'tech_clause',
                        is_tech_group=True,
                        predicate={'type': 'false'},
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            True,
            id='technical group clause',
        ),
        pytest.param(
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause', predicate={'type': 'true'},
                    ),
                ],
            ),
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause', predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'tech_clause',
                        is_tech_group=True,
                        predicate={'type': 'false'},
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            True,
            id='add technical group clause to end',
        ),
        pytest.param(
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause', predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'tech_clause',
                        is_tech_group=True,
                        predicate={'type': 'false'},
                    ),
                ],
            ),
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause', predicate={'type': 'true'},
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            True,
            id='remove technical group clause from end',
        ),
        pytest.param(
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause',
                        is_tech_group=True,
                        predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'tech_clause',
                        is_tech_group=True,
                        predicate={'type': 'false'},
                    ),
                ],
            ),
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause',
                        is_tech_group=True,
                        predicate={'type': 'true'},
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            True,
            id='all groups is technical',
        ),
        pytest.param(
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause A', predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'clause B',
                        is_tech_group=True,
                        predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'clause C', predicate={'type': 'false'},
                    ),
                ],
            ),
            experiment.generate(
                clauses=[
                    experiment.make_clause(
                        'clause A', predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'clause BA',
                        is_tech_group=True,
                        predicate={'type': 'true'},
                    ),
                    experiment.make_clause(
                        'clause C', predicate={'type': 'false'},
                    ),
                ],
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            True,
            id='change title for technical group',
        ),
        pytest.param(
            experiment.generate(
                consumers=experiment.make_consumers('t1', 't2'),
            ),
            experiment.generate(
                consumers=experiment.make_consumers('t2', 't1'),
                prestable_flow=experiment.make_prestable_flow(
                    WAIT_ON_PRESTABLE,
                ),
            ),
            False,
            False,
            id='changed consumers sort order',
        ),
        pytest.param(
            experiment.generate(
                match_predicate=experiment.inset_predicate([1]),
            ),
            experiment.generate(
                match_predicate=experiment.DEFAULT_PREDICATE,
                prestable_flow=experiment.make_prestable_flow(
                    wait_on_prestable=10,
                ),
            ),
            True,
            False,
            id='significant changes with wait prestable',
        ),
    ],
)
def test_field_changes(
        current_dict,
        new_model,
        significant_for_biz_revision,
        significant_for_wait_prestable,
):
    assert (
        biz_revision.are_significant_changes(
            api.RawExperiment.deserialize(current_dict),
            api.RawExperiment.deserialize(new_model),
        )
        == significant_for_biz_revision
    )
    assert (
        status_wait_prestable.need_warning_wait_prestable(
            api.RawExperiment.deserialize(current_dict),
            api.RawExperiment.deserialize(new_model),
        )
        == significant_for_wait_prestable
    )
