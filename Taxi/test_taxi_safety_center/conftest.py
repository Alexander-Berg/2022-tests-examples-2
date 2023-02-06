# pylint: disable=redefined-outer-name
import dataclasses
import random
from typing import Any
from typing import Dict
from typing import List
from typing import Union
import uuid

from mypy_extensions import TypedDict
import pytest

from taxi.clients import archive_api
from taxi.clients import experiments3
from taxi.clients import personal
from taxi.clients import user_api

import taxi_safety_center.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from taxi_safety_center.repositories import accidents
from test_taxi_safety_center import data_generators

pytest_plugins = ['taxi_safety_center.generated.service.pytest_plugins']


@pytest.fixture
def mock_archive_response(monkeypatch):
    def mock_archive(order_response, get_rows_response=None):
        if get_rows_response is None:
            get_rows_response = order_response

        async def get_order_patch(*args, **kwargs):
            return order_response

        monkeypatch.setattr(
            archive_api.ArchiveApiClient, 'get_order_by_id', get_order_patch,
        )

        async def get_rows_patch(*args, **kwargs):
            return [get_rows_response] if get_rows_response is not None else []

        monkeypatch.setattr(
            archive_api.ArchiveApiClient, 'select_rows', get_rows_patch,
        )

    return mock_archive


@pytest.fixture
def mock_experiments_response(monkeypatch):
    EXPERIMENT_VALUE = Dict[str, Any]
    EXPERIMENT = TypedDict(  # pylint: disable=C0103
        'EXPERIMENT', {'name': str, 'value': EXPERIMENT_VALUE},
    )

    @dataclasses.dataclass
    class Response:
        name: str
        value: EXPERIMENT_VALUE = dataclasses.field(default_factory=dict)

    def mock_experiment(experiments: List[Union[str, EXPERIMENT]]):
        wrapped_response = list()
        for experiment in experiments:
            if isinstance(experiment, str):
                response = Response(name=experiment)
            elif isinstance(experiment, dict):
                response = Response(
                    name=experiment['name'], value=experiment['value'],
                )
            else:
                raise ValueError('invalid experiment format')
            wrapped_response.append(response)

        async def get_values_patch(*args, **kwargs):
            return wrapped_response

        monkeypatch.setattr(
            experiments3.Experiments3Client, 'get_values', get_values_patch,
        )

    return mock_experiment


@pytest.fixture
def mock_personal_response(monkeypatch):
    def mock_personal(response: List[str]):
        async def response_patch(*args, **kwargs):
            return [
                {'phone': phone, 'id': phone + '_id'} for phone in response
            ]

        monkeypatch.setattr(
            personal.PersonalApiClient, 'bulk_store', response_patch,
        )
        monkeypatch.setattr(
            personal.PersonalApiClient, 'bulk_retrieve', response_patch,
        )

    return mock_personal


@pytest.fixture
def mock_personal_single_response(monkeypatch):
    def mock_single_personal(phone: str):
        async def response_patch(*args, **kwargs):
            return {'phone': phone, 'id': phone + '_id'}

        monkeypatch.setattr(
            personal.PersonalApiClient, 'store', response_patch,
        )
        monkeypatch.setattr(
            personal.PersonalApiClient, 'retrieve', response_patch,
        )

    return mock_single_personal


@pytest.fixture
def mock_user_api_response(monkeypatch):
    def mock_user_api(personal_phone_id):
        async def get_user_phone(*args, **kwargs):
            return {'personal_phone_id': personal_phone_id}

        monkeypatch.setattr(
            user_api.UserApiClient, 'get_user_phone', get_user_phone,
        )

    return mock_user_api


@pytest.fixture
async def new_accident(web_app):
    api_accident = data_generators.generated_accident(
        number=random.randint(0, 1337), generate_id=False,
    )
    accident = await accidents.insert_accident(
        accident=api_accident,
        order_id=str(uuid.uuid4().hex),
        user_id=str(uuid.uuid4().hex),
        yandex_uid=str(uuid.uuid4().hex),
        context=web_app['context'],
        log_extra={},
    )
    return accident
