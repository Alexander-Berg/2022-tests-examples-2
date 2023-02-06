# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import asyncio
import json


import pytest

import task_processor.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from task_processor.internal import models

pytest_plugins = [
    'task_processor.generated.service.provider_client.pytest_plugin',
    'task_processor.generated.service.pytest_plugins',
]


@pytest.fixture
def get_job(web_context):
    async def _wrapper(job_id):
        query = web_context.postgres_queries['jobs_get_one.sql']
        master_pool = web_context.pg.master_pool
        jobs = await master_pool.fetch(query, job_id)
        assert len(jobs) == 1
        return jobs[0]

    return _wrapper


@pytest.fixture
def add_providers(web_context):
    async def _wrapper(name, tvm_id, hostname, tvm_name=None):
        if not tvm_name:
            tvm_name = name
        query = web_context.postgres_queries['providers_add.sql']
        master_pool = web_context.pg.master_pool
        providers = await master_pool.fetch(
            query, name, tvm_id, hostname, tvm_name,
        )
        return models.Provider.deserialize(dict(providers[0]))

    return _wrapper


@pytest.fixture
def get_providers(web_context):
    async def _wrapper(id_):
        query = web_context.postgres_queries['providers_get_by_id.sql']
        master_pool = web_context.pg.master_pool
        providers = await master_pool.fetch(query, id_)
        if providers:
            return models.Provider.deserialize(dict(providers[0]))
        return providers

    return _wrapper


@pytest.fixture
def get_recipe(web_context):
    async def _wrapper(id_):
        async with web_context.pg.master_pool.acquire() as conn:
            async with conn.transaction():
                recipe = await web_context.service_manager.recipes.get_by_id(
                    id_, conn=conn,
                )
        return recipe

    return _wrapper


@pytest.fixture
def get_cubes_by_provider_id(web_context):
    async def _wrapper(provider_id):
        query = web_context.postgres_queries['cubes_get_by_provider_id.sql']
        master_pool = web_context.pg.master_pool
        cubes = await master_pool.fetch(query, provider_id)
        cubes_model = []
        if cubes:
            for cube in cubes:
                cube = dict(cube)
                cube['needed_parameters'] = json.loads(
                    cube['needed_parameters'],
                )
                cube['optional_parameters'] = json.loads(
                    cube['optional_parameters'],
                )
                cube['output_parameters'] = json.loads(
                    cube['output_parameters'],
                )
                cube_model = models.Cube.deserialize(dict(cube))
                cubes_model.append(cube_model)
        return cubes_model

    return _wrapper


@pytest.fixture
def get_tasks_by_job_id(web_context):
    async def _wrapper(job_id):
        query = web_context.postgres_queries['tasks_get_by_job_id.sql']
        master_pool = web_context.pg.master_pool
        tasks = await master_pool.fetch(query, job_id)
        return tasks

    return _wrapper


@pytest.fixture
async def make_iterations(web_context, get_job, get_tasks_by_job_id):
    async def wrapped(job_id, num=10):
        waited = 0
        while True:
            if waited >= num:
                break
            job_info = await get_job(job_id)
            status = job_info['status']

            if status != 'in_progress':
                break
            if job_info['error_message']:
                break
            tasks = await get_tasks_by_job_id(job_id)
            for task in tasks:
                if task['error_message']:
                    break

            waited += 1
            await asyncio.sleep(1)

    return wrapped


@pytest.fixture
def add_cube(web_context):
    async def _wrapper(
            name,
            provider_id,
            needed_parameters,
            optional_parameters,
            output_parameters,
    ):
        query = web_context.postgres_queries['cubes_add.sql']
        master_pool = web_context.pg.master_pool
        data = {
            'name': name,
            'provider_id': provider_id,
            'needed_parameters': needed_parameters,
            'optional_parameters': optional_parameters,
            'output_parameters': output_parameters,
        }
        cube_id = await master_pool.fetch(query, json.dumps(data))
        return cube_id

    return _wrapper
