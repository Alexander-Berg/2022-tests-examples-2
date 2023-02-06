import pytest

from taxi_exp.generated.service.swagger.models.api import common as model_api
from taxi_exp.lib import biz_revision
from taxi_exp.lib import trait_tags
from test_taxi_exp.helpers import experiment

SCHEMA = """additionalProperties: false
properties:
   enabled:
      type: boolean
"""

NO_CLAUSES = experiment.generate(
    clauses=[],
    trait_tags=[trait_tags.ANALYTICAL_TAG],
    default_value={},
    schema=SCHEMA,
)

TWO_CLAUSES = experiment.generate(
    trait_tags=[trait_tags.ANALYTICAL_TAG],
    default_value={},
    clauses=[
        experiment.make_clause(
            'title', predicate=experiment.mod_sha1_predicate(), value={},
        ),
        experiment.make_clause(
            'title_2', predicate=experiment.mod_sha1_predicate(), value={},
        ),
    ],
    schema=SCHEMA,
)

TWO_CLAUSES_WITH_TECH = experiment.generate(
    trait_tags=[trait_tags.ANALYTICAL_TAG],
    default_value={},
    clauses=[
        experiment.make_clause(
            'title', predicate=experiment.mod_sha1_predicate(), value={},
        ),
        experiment.make_clause(
            'title_2',
            predicate=experiment.mod_sha1_predicate(),
            value={},
            is_tech_group=True,
        ),
    ],
    schema=SCHEMA,
)


@pytest.mark.parametrize(
    'body,need_remove_analytical',
    [
        pytest.param(NO_CLAUSES, True, id='no clauses'),
        pytest.param(TWO_CLAUSES, False, id='two clauses'),
        pytest.param(
            TWO_CLAUSES_WITH_TECH, True, id='two clauses with tech group',
        ),
    ],
)
def test(body, need_remove_analytical):
    assert (
        biz_revision.need_remove_analytical(
            model_api.RawExperiment.deserialize(body, allow_extra=True),
        )
        == need_remove_analytical
    )
