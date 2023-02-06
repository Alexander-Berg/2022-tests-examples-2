# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest
from shortcuts_plugins import *  # noqa: F403 F401

from tests_shortcuts import consts
from tests_shortcuts import helpers


@pytest.fixture()
def add_experiment(experiments3):
    def _wrapper(name, value, consumers=None, predicates=None):
        if predicates is None:
            predicates = [{'type': 'true'}]
        if consumers is None:
            consumers = ['shortcuts/shortcuts']

        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=name,
            consumers=consumers,
            clauses=[
                {
                    'title': 'test_experiment',
                    'value': value,
                    'predicate': {
                        'init': {'predicates': predicates},
                        'type': 'all_of',
                    },
                },
            ],
        )

    return _wrapper


@pytest.fixture()
def add_config(experiments3):
    def _wrapper(name, value):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=name,
            consumers=['shortcuts/shortcuts'],
            default_value=value,
            clauses=[],
        )

    return _wrapper


# pylint: disable=redefined-outer-name
@pytest.fixture(name='add_appearance_experiments')
def _add_bricks_and_buttons_appearance_experiment_fixture(add_experiment):
    def _wrapper(
            value=None,
            overrides=None,
            predicates=None,
            appearance_ext=None,
            with_attributed_title=False,
    ):
        if value is None:
            value = {
                scenario.name: helpers.generate_brick_appearance(
                    scenario=scenario,
                    overrides=overrides,
                    with_attributed_title=with_attributed_title,
                )
                for scenario in helpers.Scenarios
            }
        if appearance_ext is not None:
            value.update(appearance_ext)
        add_experiment(
            consts.SUPERAPP_BRICKS_APPEARANCE_EXPERIMENT,
            value,
            predicates=predicates,
        )
        add_experiment(
            consts.SUPERAPP_BUTTONS_APPEARANCE_EXPERIMENT,
            value,
            predicates=predicates,
        )

    return _wrapper
