# pylint: disable=import-error
import typing

from grocery_mocks.utils.handle_context import HandleContext
import pytest

from .. import consts


_CONFIG_NAME = 'GROCERY_TAKEOUT_ENTITIES'

_HANDLE_LOAD_IDS = '/load-ids'
_HANDLE_LOAD_BY_ID = '/load-by-id'
_HANDLE_DELETE_BY_ID = '/delete-by-id'
_HANDLE_STATUS = '/status'


class EntityContext:
    def __init__(self, mockserver, taxi_config, entity_type: str):
        self.mockserver = mockserver
        self.taxi_config = taxi_config
        self.entity_type = entity_type

        self.load_ids = HandleContext()
        self.load_by_id = HandleContext()
        self.delete_by_id = HandleContext()
        self.status = HandleContext()

        self._config_init()
        self._config_update_endpoints(
            load_by_id=dict(path=_HANDLE_LOAD_BY_ID),
            delete_by_id=dict(path=_HANDLE_DELETE_BY_ID),
        )

    def mock_load_ids(
            self,
            mapping: typing.Dict[str, typing.List[str]],
            id_name=consts.ENTITY_ID_NAME,
            limit: int = None,
    ):
        self._config_update_endpoints(load_ids=dict(path=_HANDLE_LOAD_IDS))

        @self.mockserver.json_handler(self._uri(_HANDLE_LOAD_IDS))
        def _handler(request):
            self.load_ids(request)

            body = request.json

            assert id_name in body
            assert 'till_dt' in body

            ids = mapping.get(body[id_name]) or []
            offset = body.get('cursor', {}).get('offset', 0)
            offset_max = offset + (limit or len(ids))

            cursor = None
            if offset_max < len(ids):
                cursor = dict(offset=offset_max)

            return {'ids': ids[offset:offset_max], 'cursor': cursor}

    def mock_load_by_id(
            self,
            mapping: typing.Dict[str, typing.List[dict]] = None,
            id_name=consts.ENTITY_ID_NAME,
            status_code=200,
    ):
        mapping = mapping or {}

        @self.mockserver.json_handler(self._uri(_HANDLE_LOAD_BY_ID))
        def _handler(request):
            self.load_by_id(request)

            body = request.json

            assert id_name in body

            if status_code != 200:
                return self.mockserver.make_response(
                    json={}, status=status_code,
                )

            entity_objects = mapping.get(body[id_name]) or []
            entity_objects = [
                {
                    'id': it['id'],
                    'data': it.get('data', {}),
                    'sensitive_data': it.get('sensitive_data'),
                }
                for it in entity_objects
            ]

            return {'objects': entity_objects}

    def mock_delete_by_id(
            self, id_name=consts.ENTITY_ID_NAME, status_code=200,
    ):
        @self.mockserver.json_handler(self._uri(_HANDLE_DELETE_BY_ID))
        def _handler(request):
            self.delete_by_id(request)

            body = request.json

            assert id_name in body

            if status_code != 200:
                return self.mockserver.make_response(
                    json={}, status=status_code,
                )

            return {}

    def mock_status(self, status: str):
        self._config_update_endpoints(status=dict(path=_HANDLE_STATUS))

        self.status.mock_response(status=status)

        @self.mockserver.json_handler(self._uri(_HANDLE_STATUS))
        def _handler(request):
            self.status(request)

            return self.status.response

    def _uri(self, handle):
        return f'/entity/{self.entity_type}{handle}'

    def _config_init(self):
        config = self.taxi_config.get(_CONFIG_NAME, {})
        config[self.entity_type] = {
            'base_url': f'{self.mockserver.base_url}entity/{self.entity_type}',
            'tvm_name': 'mock',
            'endpoints': {},
        }
        self.taxi_config.set_values({_CONFIG_NAME: config})

    def _config_update_endpoints(self, **endpoints):
        config = self.taxi_config.get(_CONFIG_NAME)
        config[self.entity_type]['endpoints'].update(endpoints)


class Context:
    def __init__(self, mockserver, taxi_config):
        self._mockserver = mockserver
        self._taxi_config = taxi_config
        self._entities: typing.Dict[str, EntityContext] = {}

    @property
    def orders(self):
        return self['orders']

    def __getitem__(self, entity_type):
        entity = self._entities.get(entity_type)
        if entity is None:
            entity = EntityContext(
                self._mockserver, self._taxi_config, entity_type,
            )
            self._entities[entity_type] = entity
        return entity


@pytest.fixture
def mock_entities(mockserver, taxi_config):
    return Context(mockserver, taxi_config)
