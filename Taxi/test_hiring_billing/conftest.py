# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime
import typing

import pytest

import hiring_billing.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_billing.generated.service.pytest_plugins']


# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
@pytest.fixture
def create_contragent_draft(web_app_client):
    """Создание черновика контрагента"""

    async def _wrapper(
            data, contragent_id: typing.Optional[str] = None,
    ) -> str:
        if contragent_id is not None:
            data['contragent_id'] = contragent_id

        response = await web_app_client.post('/v1/contragent/', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def commit_contragent_draft(web_app_client):
    """Коммит черновика контрагента"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post(
            '/v1/contragent/commit/', json=data,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def create_contragent(web_app_client):
    """Создание контрагента"""

    async def _wrapper(
            data,
            contragent_id: typing.Optional[str] = None,
            category: typing.Optional[str] = None,
            name: typing.Optional[str] = None,
    ) -> str:
        if contragent_id is not None:
            data['contragent_id'] = contragent_id
        if category is not None:
            data['category'] = category
        if name is not None:
            data['name'] = name

        response = await web_app_client.post('/v1/contragent/', json=data)
        assert response.status == 200, await response.text()
        approve = await response.json()

        response = await web_app_client.post(
            '/v1/contragent/commit/', json=approve['data'],
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_contragent(web_app_client):
    """Получение контрагента"""

    async def _wrapper(contragent_id: str) -> str:
        response = await web_app_client.get(
            '/v1/contragent/', params={'contragent_id': contragent_id},
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def list_contragents(web_app_client):
    """Получение списка контрагентов"""

    async def _wrapper(
            categories: typing.Optional[typing.List[str]] = None,
            offset: typing.Optional[int] = None,
            limit: typing.Optional[int] = None,
    ) -> str:
        params = {}
        if categories is not None:
            params['categories'] = ','.join(categories)
        if offset is not None:
            params['offset'] = str(offset)
        if limit is not None:
            params['limit'] = str(limit)

        response = await web_app_client.get(
            '/v1/contragents/list/', params=params,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def create_contract_draft(
        web_app_client, load_json, mock_hiring_tariffs, mock_taxi_tariffs,
):
    """Создание черновика договора"""

    async def _wrapper(
            data,
            contract_id: typing.Optional[str] = None,
            contragent_id: typing.Optional[str] = None,
            tariff_file: typing.Optional[str] = 'tariff.json',
            zones_file: typing.Optional[str] = 'zones.json',
    ) -> str:
        if contract_id is not None:
            data['contract_id'] = contract_id
        if contragent_id is not None:
            data['contragent_id'] = contragent_id

        @mock_hiring_tariffs('/v1/tariff/')
        async def handler1(request):  # pylint: disable=unused-variable
            return load_json(tariff_file)

        @mock_taxi_tariffs('/v1/tariff_zones')
        async def handler2(request):  # pylint: disable=unused-variable
            return load_json(zones_file)

        response = await web_app_client.post('/v1/contract/', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def commit_contract_draft(web_app_client):
    """Коммит черновика договора"""

    async def _wrapper(data) -> str:
        response = await web_app_client.post('/v1/contract/commit/', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def create_contract(
        web_app_client, load_json, mock_hiring_tariffs, mock_taxi_tariffs,
):
    """Создание договора"""

    async def _wrapper(
            data,
            contract_id: typing.Optional[str] = None,
            contragent_id: typing.Optional[str] = None,
            medium: typing.Optional[str] = None,
            geo: typing.Optional[typing.List[str]] = None,
            start_ts: typing.Optional[datetime.datetime] = None,
            finish_ts: typing.Optional[datetime.datetime] = None,
            tariff_file: typing.Optional[str] = 'tariff.json',
            zones_file: typing.Optional[str] = 'zones.json',
    ) -> str:
        if contract_id is not None:
            data['contract_id'] = contract_id
        if contragent_id is not None:
            data['contragent_id'] = contragent_id
        if medium is not None:
            data['medium'] = medium
        if geo is not None:
            data['geo'] = geo
        if start_ts is not None:
            data['start_ts'] = int(start_ts.timestamp())
        if finish_ts is not None:
            data['finish_ts'] = int(finish_ts.timestamp())

        @mock_hiring_tariffs('/v1/tariff/')
        async def handler1(request):  # pylint: disable=unused-variable
            return load_json(tariff_file)

        @mock_taxi_tariffs('/v1/tariff_zones')
        async def handler2(request):  # pylint: disable=unused-variable
            return load_json(zones_file)

        response = await web_app_client.post('/v1/contract/', json=data)
        assert response.status == 200, await response.text()
        approve = await response.json()

        response = await web_app_client.post(
            '/v1/contract/commit/', json=approve['data'],
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_contract(web_app_client):
    """Получение договора"""

    async def _wrapper(contract_id: str) -> str:
        response = await web_app_client.get(
            '/v1/contract/', params={'contract_id': contract_id},
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def list_contracts(web_app_client):
    """Получение списка договоров"""

    async def _wrapper(
            contragent_id: typing.Optional[str] = None,
            medium: typing.Optional[str] = None,
            geo: typing.Optional[str] = None,
            time_ts: typing.Optional[datetime.datetime] = None,
            status: typing.Optional[str] = None,
            search: typing.Optional[str] = None,
            offset: typing.Optional[int] = None,
            limit: typing.Optional[int] = None,
    ) -> str:
        params: typing.Dict[str, typing.Any] = {}
        if contragent_id is not None:
            params['contragent_id'] = contragent_id
        if medium is not None:
            params['medium'] = medium
        if geo is not None:
            params['geo'] = geo
        if time_ts is not None:
            params['time_ts'] = int(time_ts.timestamp())
        if status is not None:
            params['status'] = status
        if search is not None:
            params['search'] = search
        if offset is not None:
            params['offset'] = str(offset)
        if limit is not None:
            params['limit'] = str(limit)

        response = await web_app_client.get(
            '/v1/contracts/list/', params=params,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def calculate_events(web_app_client, load_json, mock_parks_replica):
    """Расчет"""

    async def _wrapper(
            data: dict,
            id_file: typing.Optional[str] = 'billing_client_id.json',
    ) -> str:
        @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
        async def handler(request):  # pylint: disable=unused-variable
            return load_json(id_file)

        response = await web_app_client.post(
            '/v1/events/calculate/', json=data,
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper
