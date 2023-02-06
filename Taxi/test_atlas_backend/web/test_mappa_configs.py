import json
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from aiohttp import test_utils
import pytest


@pytest.fixture(name='mappa_configs_data')
def mappa_configs_data_fixture(open_file):
    with open_file('mappa_configs_data.json') as mappa_configs_data_json:
        return json.load(mappa_configs_data_json)


@pytest.fixture(name='non_existent_mappa_config')
def non_existent_config_fixture(open_file):
    with open_file('non_existent_config.json') as non_existent_config_json:
        return json.load(non_existent_config_json)


async def get_mappa_config(
        web_app_client: test_utils.TestClient, code: str,
) -> Optional[dict]:
    path = '/api/v1/mappa/configs'
    params = {'code': code}
    response = await web_app_client.get(path, params=params)
    if response.status == 200:
        return await response.json()

    return None


class TestGetMappaConfig:
    async def request(
            self, web_app_client: test_utils.TestClient, code: str,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/mappa/configs'
        params = {'code': code}
        return await web_app_client.get(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    @pytest.mark.parametrize(
        'code,expected_status',
        [
            ('test_config_1', 200),
            ('test_config_2', 200),
            ('non_existent_config', 404),
            ('test_config_10', 404),
        ],
    )
    async def test_get_search(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            code: str,
            expected_status: int,
    ):
        response = await self.request(web_app_client, code)
        assert response.status == expected_status

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    @pytest.mark.parametrize('config_ind', [0, 1, 2, 3])
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            mappa_configs_data: List[List[Any]],
            config_ind: int,
    ):
        config_code: str = mappa_configs_data[config_ind][0]
        config: dict = mappa_configs_data[config_ind][1]
        response = await self.request(web_app_client, config_code)
        assert response.status == 200
        assert await response.json() == config

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_get_not_found(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ):
        code = 'non_existent_config'
        response = await self.request(web_app_client, code)
        assert response.status == 404
        err = await response.json()
        assert err['message'] == f'Unknown Mappa config with code {code}'


class TestGetMappaConfigsList:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            limit: int,
            offset: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/mappa/configs/list'
        params = {'limit': limit, 'offset': offset}
        return await web_app_client.get(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    @pytest.mark.parametrize(
        'limit,offset,configs_inds_range',
        [(1, 0, (0, 1)), (4, 0, (0, 4)), (2, 1, (1, 3)), (3, 3, (3, 4))],
    )
    async def test_get_list(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            mappa_configs_data: List[List[Any]],
            limit: int,
            offset: int,
            configs_inds_range: Tuple[int, int],
    ):
        configs = mappa_configs_data[
            configs_inds_range[0] : configs_inds_range[1]
        ]
        response = await self.request(web_app_client, limit, offset)
        assert response.status == 200
        assert await response.json() == [
            config[1]['meta'] for config in configs
        ]


class TestCreateMappaConfig:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            code: str,
            config: dict,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/mappa/configs'
        params = {'code': code}
        return await web_app_client.post(path, params=params, json=config)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            non_existent_mappa_config: dict,
    ):
        code = 'non_existent_config'
        config_before = await get_mappa_config(web_app_client, code)
        assert config_before is None

        response = await self.request(
            web_app_client, code, non_existent_mappa_config,
        )

        assert response.status == 201

        config_before = await get_mappa_config(web_app_client, code)
        assert config_before == non_existent_mappa_config

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_create_existent(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            mappa_configs_data: List[List[Any]],
    ):
        code = mappa_configs_data[0][0]
        config = mappa_configs_data[0][1]

        config_before = await get_mappa_config(web_app_client, code)
        assert config_before is not None

        response = await self.request(web_app_client, code, config)

        assert response.status == 400
        err = await response.json()
        assert (
            err['message'] == f'Mappa config with code {code} already exists'
        )

        config_after = await get_mappa_config(web_app_client, code)
        assert config_before == config_after


class TestUpdateMappaConfig:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            code: str,
            config: dict,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/mappa/configs'
        params = {'code': code}
        return await web_app_client.patch(path, params=params, json=config)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            mappa_configs_data: List[List[Any]],
            non_existent_mappa_config: dict,
    ):
        code = mappa_configs_data[0][0]
        config = non_existent_mappa_config

        config_before = await get_mappa_config(web_app_client, code)
        assert config_before is not None

        response = await self.request(web_app_client, code, config)

        assert response.status == 201
        config_after = await get_mappa_config(web_app_client, code)
        assert config_after == non_existent_mappa_config

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_update_non_existent(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            non_existent_mappa_config: dict,
    ):
        code = 'non_existent_config'

        config_before = await get_mappa_config(web_app_client, code)
        assert config_before is None

        response = await self.request(
            web_app_client, code, non_existent_mappa_config,
        )
        assert response.status == 404

        err = await response.json()
        assert err['message'] == f'Unknown Mappa config with code {code}'

        config_after = await get_mappa_config(web_app_client, code)
        assert config_before == config_after

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    @pytest.mark.parametrize(
        'username,code,expected_status',
        [
            ('raifox', 'test_config_1', 201),  # owner
            ('raifox', 'test_config_2', 403),  # not owner
            ('test_user', 'test_config_1', 403),  # not owner
            ('test_user', 'test_config_2', 201),  # owner
            ('omnipotent_user', 'test_config_1', 201),  # superuser
            ('omnipotent_user', 'test_config_2', 201),  # superuser
        ],
    )
    async def test_update_permissions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            non_existent_mappa_config: dict,
            username: str,
            code: str,
            expected_status: int,
    ):
        response = await self.request(
            web_app_client, code, non_existent_mappa_config,
        )
        assert response.status == expected_status


class TestDeleteMappaConfig:
    async def request(
            self, web_app_client: test_utils.TestClient, code: str,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/mappa/configs'
        params = {'code': code}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            mappa_configs_data: List[List[Any]],
    ):
        code = mappa_configs_data[0][0]

        config_before = await get_mappa_config(web_app_client, code)
        assert config_before is not None

        response = await self.request(web_app_client, code)

        assert response.status == 201
        config_after = await get_mappa_config(web_app_client, code)
        assert config_after is None

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    async def test_delete_non_existent(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ):
        code = 'non_existent_config'

        config_before = await get_mappa_config(web_app_client, code)
        assert config_before is None

        response = await self.request(web_app_client, code)
        assert response.status == 404

        err = await response.json()
        assert err['message'] == f'Unknown Mappa config with code {code}'

        config_after = await get_mappa_config(web_app_client, code)
        assert config_after is None

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_mappa_configs.sql'],
    )
    @pytest.mark.parametrize(
        'username,code,expected_status',
        [
            ('raifox', 'test_config_1', 201),  # owner
            ('raifox', 'test_config_2', 403),  # not owner
            ('test_user', 'test_config_1', 403),  # not owner
            ('test_user', 'test_config_2', 201),  # owner
            ('omnipotent_user', 'test_config_1', 201),  # superuser
            ('omnipotent_user', 'test_config_2', 201),  # superuser
        ],
    )
    async def test_delete_permissions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            code: str,
            expected_status: int,
    ):
        response = await self.request(web_app_client, code)
        assert response.status == expected_status
