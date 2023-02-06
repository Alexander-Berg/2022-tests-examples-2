from sandbox.common import config as common_config
import sandbox.common.types.resource as ctr

from sandbox.tasklet.sidecars.resource_manager.lib import storage
from sandbox.tasklet.sidecars.resource_manager.handlers import base


class TestHandler(base.BaseHandler):
    """ Class for managing Sandbox resources in test runtime """
    def __init__(self, token: str or None, config: common_config.Registry):
        """
        :param token: token for Sandbox session, may be None for test runtime
        :param config: Sandbox config
        """
        super(TestHandler, self).__init__(token, config)
        self.storage = storage.Storage()

    def download_resource(self, resource_id: int) -> str:
        """ Check local storage for resource with resource_id and return path to it """
        return self.storage.resource_sync(resource_id)

    def create_resource(
        self, resource_type: str, arch: str, owner: str, attributes: dict[str, str], path: str, description: str
    ) -> dict:
        """ Copy files to local storage, create new resource in local storage and return it meta """
        return self.storage.register_resource(resource_type, arch, owner, attributes, path, description)

    def get_resources(
        self, ids: list[int], resource_type: str, state: ctr.State, owner: str, task_ids: int, any_attr: bool,
        attributes: dict[str, str], offset: int, limit: int, order: list[str]
    ) -> list[dict]:
        """ Filter resources in local storage by parameters and return """
        query = self._create_api_query(
            ids, resource_type, state, owner, task_ids, any_attr, attributes, offset, limit, order
        )
        return self.storage.filter_resources(self.storage.resources, query)
