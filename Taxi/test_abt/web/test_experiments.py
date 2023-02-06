import asyncpg
import pytest

from abt import models


async def test_db_consistency(taxi_abt_web, abt):
    await abt.state.add_experiment(experiment_type='experiment')
    await abt.state.add_experiment(experiment_type='config')

    with pytest.raises(asyncpg.exceptions.UniqueViolationError):
        await abt.state.add_experiment(experiment_type='config')


async def test_experiment_model_building(abt):
    experiment = models.Experiment.from_record(
        await abt.state.add_experiment(experiment_type='config'),
    )

    assert experiment.type == models.ExperimentType.Config
