import typing as tp
import uuid

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data

EXISTED_GROUPS = db_data.GROUPS


async def delete_group(
        web_app_client: test_utils.TestClient, group_id: int,
) -> None:
    # in case passport error, make sure that you use atlas_blackbox_mock
    params = {'group_id': group_id}
    response = await web_app_client.delete(
        '/api/v3/metric_groups', params=params,
    )
    assert response.status == 204, await response.text()


async def get_group(
        web_app_client: test_utils.TestClient, group_id: int,
) -> tp.Dict[str, tp.Any]:
    params = {'group_id': group_id}
    response = await web_app_client.get('/api/v3/metric_groups', params=params)
    assert response.status == 200, await response.text()
    return await response.json()


async def get_groups(
        web_app_client: test_utils.TestClient,
) -> tp.List[tp.Dict[str, tp.Any]]:
    response = await web_app_client.get('/api/v3/metric_groups/list')
    assert response.status == 200, await response.text()
    return await response.json()


class _NewGroupsGetter:
    def __init__(self, web_app_client: test_utils.TestClient) -> None:
        self._web_app_client = web_app_client
        self.existed_group_ids: tp.Set[int] = set()
        self.new_groups: tp.List[tp.Dict[str, tp.Any]] = []

    async def __aenter__(self):
        self.existed_group_ids = {
            group['group_id']
            for group in await get_groups(self._web_app_client)
        }
        return self

    async def __aexit__(self, *args, **kwargs):
        self.new_groups = [
            group
            for group in await get_groups(self._web_app_client)
            if group['group_id'] not in self.existed_group_ids
        ]


class TestGetMetricGroup:
    async def request(
            self, web_app_client: test_utils.TestClient, group_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metric_groups'
        params = {'group_id': group_id}
        return await web_app_client.get(path, params=params)

    async def test_get_not_existed_group(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        group_id = 1
        response = await self.request(web_app_client, group_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricGroupNotExists'
        assert (
            err['message'] == f'There is not metric group with id {group_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.parametrize('group', [group for group in EXISTED_GROUPS])
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            group: tp.Dict[str, tp.Any],
    ) -> None:
        response = await self.request(web_app_client, group['group_id'])
        assert response.status == 200, await response.text()
        group_data = await response.json()
        assert group_data == group


class TestGetMetricGroups:
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    async def test_get_list(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        response = await web_app_client.get('/api/v3/metric_groups/list')
        assert response.status == 200, await response.text()
        groups = await response.json()
        assert len(groups) == len(EXISTED_GROUPS)
        groups.sort(key=lambda group: group['group_id'])
        assert groups == sorted(
            EXISTED_GROUPS, key=lambda group: group['group_id'],
        )


class TestCreateMetricGroup:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            group_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metric_groups'
        return await web_app_client.post(path, json=group_data)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        group_data = {
            'ru_name': 'Метрики3',
            'en_name': 'Metrics3',
            'ru_description': 'Группа с метриками',
            'en_description': 'Group with metrics',
        }
        path = '/api/v3/metric_groups'
        response = await web_app_client.post(
            path, json=group_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @pytest.mark.parametrize('ru_description', [None, 'Описание 1'])
    @pytest.mark.parametrize('en_description', [None, 'Описание 2'])
    async def test_create_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
    ) -> None:
        group_data = {
            'ru_name': f'Группа {uuid.uuid4()}',
            'en_name': f'Group {uuid.uuid4()}',
        }
        if ru_description is not None:
            group_data['ru_description'] = ru_description
        if en_description is not None:
            group_data['en_description'] = en_description
        async with _NewGroupsGetter(web_app_client) as helper:
            response = await self.request(web_app_client, group_data)
            assert response.status == 201, await response.text()
        (group,) = helper.new_groups
        for key, value in group_data.items():
            assert group[key] == value
        await delete_group(web_app_client, group['group_id'])

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.parametrize(
        'ru_name', [EXISTED_GROUPS[0]['ru_name'], 'МетрикиN'],
    )
    @pytest.mark.parametrize(
        'en_name', [EXISTED_GROUPS[1]['en_name'], 'MetricsN'],
    )
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            ru_name: str,
            en_name: str,
    ) -> None:
        if ru_name == 'МетрикиN' and en_name == 'MetricsN':
            # TODO здесь бы скипать тесты, но пока что при этом валятся ошибки
            return
        group_data = {'ru_name': ru_name, 'en_name': en_name}
        response = await self.request(web_app_client, group_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::MetricGroupExists'
        ru_err = f'Metric group with ru name {ru_name} already exists'
        en_err = f'Metric group with en name {en_name} already exists'
        if ru_name == 'МетрикиN':
            assert err['message'] == en_err
        elif en_name == 'MetricsN':
            assert err['message'] == ru_err
        else:
            assert err['message'] in (en_err, ru_err)


class TestUpdateMetricGroup:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            group_id: int,
            group_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metric_groups'
        params = {'group_id': group_id}
        return await web_app_client.patch(path, params=params, json=group_data)

    @pytest.mark.parametrize('username', [None])
    async def test_update_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        group_id = 1
        path = '/api/v3/metric_groups'
        params = {'group_id': group_id}
        response = await web_app_client.patch(
            path, params=params, json={}, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_update_not_existed_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        group_id = 1  # not exists
        response = await self.request(web_app_client, group_id, {})
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricGroupNotExists'
        assert (
            err['message'] == f'There is not metric group with id {group_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.parametrize('existed_group', [EXISTED_GROUPS[0]])
    @pytest.mark.parametrize('ru_name', [None, 'Метрики3'])
    @pytest.mark.parametrize('en_name', [None, 'Metrics3'])
    @pytest.mark.parametrize(
        'ru_description', [None, 'Обновленная группа с метриками'],
    )
    @pytest.mark.parametrize(
        'en_description', [None, 'Updated group with metrics'],
    )
    async def test_update_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            existed_group: tp.Dict[str, tp.Any],
            ru_name: tp.Optional[str],
            en_name: tp.Optional[str],
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
    ) -> None:
        group_data = {}
        if ru_name is not None:
            group_data['ru_name'] = ru_name
        if en_name is not None:
            group_data['en_name'] = en_name
        if ru_description is not None:
            group_data['ru_description'] = ru_description
        if en_description is not None:
            group_data['en_description'] = en_description
        response = await self.request(
            web_app_client, existed_group['group_id'], group_data,
        )
        assert response.status == 204, await response.text()
        group = await get_group(web_app_client, existed_group['group_id'])
        for key, value in group.items():
            if key in group_data:
                assert group_data[key] == value
            else:
                assert existed_group[key] == value

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.parametrize('existed_group', [EXISTED_GROUPS[0]])
    @pytest.mark.parametrize('ru_name', [None, EXISTED_GROUPS[1]['ru_name']])
    @pytest.mark.parametrize('en_name', [None, EXISTED_GROUPS[1]['en_name']])
    @pytest.mark.parametrize(
        'ru_description', [None, 'Обновленная группа с метриками'],
    )
    @pytest.mark.parametrize(
        'en_description', [None, 'Updated group with metrics'],
    )
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            existed_group: tp.Dict[str, tp.Any],
            ru_name: tp.Optional[str],
            en_name: tp.Optional[str],
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
    ) -> None:
        if ru_name is None and en_name is None:
            # TODO здесь бы скипать тесты, но пока что при этом валятся ошибки
            return
        group_data = {}
        if ru_name is not None:
            group_data['ru_name'] = ru_name
        if en_name is not None:
            group_data['en_name'] = en_name
        if ru_description is not None:
            group_data['ru_description'] = ru_description
        if en_description is not None:
            group_data['en_description'] = en_description
        response = await self.request(
            web_app_client, existed_group['group_id'], group_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::MetricGroupExists'
        ru_err = f'Metric group with ru name {ru_name} already exists'
        en_err = f'Metric group with en name {en_name} already exists'
        if ru_name is None:
            assert err['message'] == en_err
        elif en_name is None:
            assert err['message'] == ru_err
        else:
            assert err['message'] in (en_err, ru_err)


class TestDeleteMetricGroup:
    async def request(
            self, web_app_client: test_utils.TestClient, group_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metric_groups'
        params = {'group_id': group_id}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        group_id = 1
        path = '/api/v3/metric_groups'
        params = {'group_id': group_id}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_delete_not_existed_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        group_id = 1  # not exists
        response = await self.request(web_app_client, group_id)
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.parametrize(
        'group_id', [group['group_id'] for group in EXISTED_GROUPS],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            group_id: int,
    ) -> None:
        response = await self.request(web_app_client, group_id)
        assert response.status == 204, await response.text()
        response = await web_app_client.get(
            '/api/v3/metric_groups', params={'group_id': group_id},
        )
        assert response.status == 404, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_delete_not_empty_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        group_id = 1
        response = await self.request(web_app_client, group_id)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::DeleteNotEmptyMetricGroup'
        assert err['message'] == (
            f'Can\'t delete metric group with id {group_id}, '
            'it\'s not empty'
        )
