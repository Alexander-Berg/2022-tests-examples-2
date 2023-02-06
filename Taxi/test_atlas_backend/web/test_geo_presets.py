from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from aiohttp import test_utils
import pytest

# see test_atlas_backend/web/static/default/pg_geo_presets.sql
GEO_PRESETS = [
    {
        'ru_name': 'Тестовый пресет 1',
        'en_name': 'Test preset 1',
        'ru_description': 'Некое подробное описание',
        'en_description': 'Detailed description',
        'hierarchy_type': 'br',
        'node_ids': ['br_kolpino', 'br_saintpetersburg'],
        'default_agg_method': 'agglomeration',
        'preset_type': 'private',
        'preset_id': 1,
    },
    {
        'ru_name': 'Тестовый пресет 2',
        'en_name': 'Test preset 2',
        'ru_description': 'Некое подробное описание',
        'en_description': 'Detailed description',
        'hierarchy_type': 'br',
        'node_ids': ['br_kolpino'],
        'default_agg_method': 'agglomeration',
        'preset_type': 'private',
        'preset_id': 2,
    },
    {
        'ru_name': 'Тестовый пресет 3',
        'en_name': 'Test preset 3',
        'ru_description': 'Некое подробное описание',
        'en_description': 'Detailed description',
        'hierarchy_type': 'br',
        'node_ids': ['br_kolpino'],
        'default_agg_method': 'agglomeration',
        'preset_type': 'public',
        'preset_id': 3,
    },
    {
        'ru_name': 'Тестовый пресет 4',
        'en_name': 'Test preset 4',
        'ru_description': 'Некое подробное описание',
        'en_description': 'Detailed description',
        'hierarchy_type': 'br',
        'node_ids': ['br_moscow', 'br_leningradskaja_obl'],
        'default_agg_method': 'agglomeration',
        'preset_type': 'public',
        'preset_id': 4,
    },
]


async def get_geo_preset(
        web_app_client: test_utils.TestClient, preset_id: int,
) -> Optional[dict]:
    path = '/api/v1/geo_presets'
    params = {'preset_id': preset_id}
    response = await web_app_client.get(path, params=params)
    if response.status == 200:
        return await response.json()

    return None


class TestCreatePreset:
    async def test_create_no_login(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        path = '/api/v1/geo_presets'
        data = {
            'ru_name': 'Пара городов',
            'en_name': 'Couple of cities',
            'ru_description': '',
            'en_description': '',
            'hierarchy_type': 'br',
            'node_ids': ['br_kolpino', 'br_saintpetersburg'],
            'default_agg_method': 'agglomeration',
            'preset_type': 'private',
        }
        response = await web_app_client.post(
            path, json=data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        path = '/api/v1/geo_presets'
        data = {
            'ru_name': 'Пара городов',
            'en_name': 'Couple of cities',
            'ru_description': '',
            'en_description': '',
            'hierarchy_type': 'br',
            'node_ids': ['br_kolpino', 'br_saintpetersburg'],
            'default_agg_method': 'agglomeration',
            'preset_type': 'private',
        }
        response = await web_app_client.post(path, json=data)
        assert response.status == 201, await response.text()

        preset_id = int(await response.text())
        preset = await get_geo_preset(web_app_client, preset_id)
        expected: dict = {'preset_id': preset_id, **data}
        assert preset == expected

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    @pytest.mark.parametrize(
        'username,node_ids,preset_type,expected_status',
        [
            # OK
            (
                'test_user1',
                ['br_kolpino', 'br_saintpetersburg'],
                'private',
                201,
            ),
            # test_user1 do not own superuser role to make public preset
            (
                'test_user1',
                ['br_kolpino', 'br_saintpetersburg'],
                'public',
                403,
            ),
            # test_user2 do not have access to br_saintpetersburg
            (
                'test_user2',
                ['br_kolpino', 'br_saintpetersburg'],
                'private',
                403,
            ),
            # Trying to create preset with not existing node
            ('test_user1', ['not_existing_node'], 'private', 403),
        ],
    )
    async def test_create_permissions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            node_ids: List[str],
            preset_type: str,
            expected_status: int,
    ) -> None:
        path = '/api/v1/geo_presets'
        data = {
            'ru_name': 'Пара городов',
            'en_name': 'Couple of cities',
            'ru_description': '',
            'en_description': '',
            'hierarchy_type': 'br',
            'node_ids': node_ids,
            'default_agg_method': 'agglomeration',
            'preset_type': preset_type,
        }
        response = await web_app_client.post(path, json=data)
        assert response.status == expected_status, await response.text()


class TestGetPreset:
    async def request(
            self, web_app_client: test_utils.TestClient, preset_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/geo_presets'
        params = {'preset_id': preset_id}
        return await web_app_client.get(path, params=params)

    async def test_get_not_found(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        response = await self.request(web_app_client, preset_id=100)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::PresetNotExists'
        assert err['message'] == 'There is no preset with id=100'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_geo_presets.sql'],
    )
    @pytest.mark.parametrize(
        'username,test_preset,expected_status',
        [
            ('test_user1', GEO_PRESETS[0], 200),  # owner of preset
            ('test_user1', GEO_PRESETS[1], 403),  # other user private preset
            ('test_user1', GEO_PRESETS[2], 200),  # public preset
            # superuser could see other user private preset
            ('omnipotent_user', GEO_PRESETS[0], 200),
        ],
    )
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            test_preset: Dict[str, Any],
            expected_status,
    ) -> None:
        response = await self.request(
            web_app_client, preset_id=test_preset['preset_id'],
        )
        assert response.status == expected_status, await response.text()

        if expected_status == 200:
            preset = await response.json()
            assert preset == test_preset


class TestDeletePreset:
    async def request(
            self, web_app_client: test_utils.TestClient, preset_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/geo_presets'
        params = {'preset_id': preset_id}
        return await web_app_client.delete(path, params=params)

    async def test_delete_not_existed(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        response = await self.request(web_app_client, preset_id=10)
        assert response.status == 404, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    async def test_delete(
            self, web_app_client: test_utils.TestClient, atlas_blackbox_mock,
    ) -> None:
        preset_id = 3
        preset_before = await get_geo_preset(
            web_app_client, preset_id=preset_id,
        )
        assert preset_before is not None

        response = await self.request(web_app_client, preset_id=preset_id)
        assert response.status == 204, await response.text()

        preset_after = await get_geo_preset(
            web_app_client, preset_id=preset_id,
        )
        assert preset_after is None

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    @pytest.mark.parametrize(
        'username,preset_id,expected_status',
        [
            # test_user1 could delete his private preset
            ('test_user1', 1, 204),
            # test_user1 could not delete private preset of other user
            ('test_user1', 2, 403),
            # test_user2 could delete his private preset
            ('test_user2', 2, 204),
            # test_user2 could not delete public preset
            ('test_user1', 3, 403),
            # superuser could delete public preset
            ('omnipotent_user', 3, 204),
            # superuser could delete private preset of other user
            ('omnipotent_user', 1, 204),
        ],
    )
    async def test_delete_permissions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            preset_id: int,
            expected_status: int,
    ) -> None:
        response = await self.request(web_app_client, preset_id=preset_id)
        assert response.status == expected_status, await response.text()


class TestUpdatePreset:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            preset_id: int,
            data: dict,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/geo_presets'
        params = {'preset_id': preset_id}
        return await web_app_client.patch(path, params=params, json=data)

    async def test_update_not_existed(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        response = await self.request(web_app_client, preset_id=100, data={})
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::PresetNotExists'
        assert err['message'] == 'There is no preset with id=100'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        update_data = {
            'ru_name': 'Переименованный пресет',
            'en_name': 'Renamed preset',
            'ru_description': 'Другое описание',
            'en_description': 'Other description',
            'node_ids': ['br_moscow'],
        }
        response = await self.request(
            web_app_client, preset_id=1, data=update_data,
        )
        assert response.status == 204, await response.text()

        preset = await get_geo_preset(web_app_client, preset_id=1)
        expected = {**GEO_PRESETS[0], **update_data}
        assert preset == expected

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    @pytest.mark.parametrize(
        'username,preset_id,update_data,expected_status',
        [
            # test_user1 owns first preset, and it is private
            ('test_user1', 1, {'node_ids': ['br_saintpetersburg']}, 204),
            # test_user1 do not have permissions on br_moscow node
            ('test_user1', 1, {'node_ids': ['br_moscow']}, 403),
            # test_user1 is not superuser to make preset public
            ('test_user1', 1, {'preset_type': 'public'}, 403),
            # test_user1 cannot change private preset of test_user2
            ('test_user1', 2, {'node_ids': ['br_saintpetersburg']}, 403),
            # should not be able to add not valid node
            # probably should be BadRequest rather than Forbidden
            ('test_user1', 1, {'node_ids': ['not_existing_node']}, 403),
        ],
    )
    async def test_update_permissions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            preset_id: int,
            update_data: dict,
            expected_status: int,
    ) -> None:
        response = await self.request(
            web_app_client, preset_id=preset_id, data=update_data,
        )
        assert response.status == expected_status, await response.text()


def _result_item(preset_id: int, has_access: bool) -> dict:
    result: dict = {**GEO_PRESETS[preset_id], 'has_access': has_access}
    return result


class TestListPresetAdmin:
    async def request(self, web_app_client: test_utils.TestClient) -> list:
        path = '/api/v1/geo_presets/list_admin'
        response = await web_app_client.get(path)
        assert response.status == 200, await response.text()
        return await response.json()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_hierarchy.sql', 'pg_geo_presets.sql'],
    )
    @pytest.mark.parametrize(
        'username,expected_results',
        [
            (
                'test_user1',
                [
                    _result_item(preset_id=0, has_access=True),
                    _result_item(preset_id=2, has_access=True),
                    _result_item(preset_id=3, has_access=False),
                ],
            ),
            (
                'test_user2',
                [
                    _result_item(preset_id=1, has_access=True),
                    _result_item(preset_id=2, has_access=True),
                    _result_item(preset_id=3, has_access=False),
                ],
            ),
            (
                'omnipotent_user',
                [
                    _result_item(preset_id=2, has_access=True),
                    _result_item(preset_id=3, has_access=True),
                ],
            ),
        ],
    )
    async def test_list_admin(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            expected_results,
    ) -> None:
        presets = sorted(
            await self.request(web_app_client),
            key=lambda item: item['preset_id'],
        )
        assert presets == expected_results
