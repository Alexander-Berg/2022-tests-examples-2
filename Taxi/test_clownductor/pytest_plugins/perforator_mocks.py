import itertools
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

import pytest

from generated.models import clowny_perforator as perforator_models

from clownductor.internal import perforator


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


class BadRequest(Exception):
    pass


class MockContext:
    POSSIBLE_ENVIRONMENTS = perforator.ENVIRONMENTS

    def __init__(self):
        self._services: Dict[str, perforator_models.Service] = {}
        self._rules: List[perforator_models.RulesListItem] = []
        self._id_generator = itertools.count(1)
        self._rule_id_generator = itertools.count(1)
        self._env_id_generator = itertools.count(1)

    @property
    def services(self) -> Iterator[perforator_models.Service]:
        yield from self._services.values()

    @property
    def rules(self) -> Iterator[perforator_models.RulesListItem]:
        yield from self._rules

    def get_by_id(self, service_id: int) -> perforator_models.Service:
        for service in self._services.values():
            if service.id == service_id:
                return service
        raise NotFound

    def add_rules(
            self, source: str, destinations: List[str],
    ) -> perforator_models.CreateRulesResponse:
        rules = []
        status = 'succeeded'
        for destination in destinations:
            for env_type in self.POSSIBLE_ENVIRONMENTS:
                rule = self.add_env_rule(source, destination, env_type)
                if rule:
                    rules.append(rule)
                else:
                    status = 'partially_completed'
        return perforator_models.CreateRulesResponse(
            created_rules=rules, status=status,
        )

    def add_env_rule(
            self, source: str, destination: str, env_type: str,
    ) -> Optional[perforator_models.RulesListItem]:
        if env_type not in self.POSSIBLE_ENVIRONMENTS:
            raise BadRequest(env_type)
        cache = {
            (rule.source.tvm_name, rule.destination.tvm_name, rule.env_type)
            for rule in self._rules
        }
        if (source, destination, env_type) in cache:
            return None
        rule_source = self._create_rule_source(source, env_type)
        rule_destination = self._create_rule_source(destination, env_type)
        if not rule_source or not rule_destination:
            return None
        created_rule = perforator_models.RulesListItem(
            destination=rule_destination,
            env_type=env_type,
            rule_id=next(self._rule_id_generator),
            source=rule_source,
        )
        self._rules.append(created_rule)
        return created_rule

    def _create_rule_source(
            self, tvm_name: str, env_type: str,
    ) -> Optional[perforator_models.RuleSource]:
        if tvm_name not in self._services:
            raise BadRequest(tvm_name)
        tvm_service = self._services[tvm_name]
        env = next(
            (
                env
                for env in tvm_service.environments
                if env.env_type == env_type
            ),
            None,
        )
        if not env:
            return None
        return perforator_models.RuleSource(
            environment_id=env.id,
            id=tvm_service.id,
            tvm_id=env.tvm_id,
            tvm_name=tvm_name,
        )

    def edit_service(
            self,
            service_id: int,
            clown_service: perforator_models.ClownService,
    ) -> perforator_models.Service:
        service = self.get_by_id(service_id)
        service.clown_service = clown_service
        return service

    def add_environment(
            self, service_id: int, env_type: str, tvm_id: int,
    ) -> perforator_models.Environment:
        service = self.get_by_id(service_id)
        for env in service.environments:
            if env.env_type == env_type:
                raise Conflict
        environment = perforator_models.Environment(
            env_type, next(self._env_id_generator), tvm_id,
        )
        service.environments.append(environment)
        return environment

    def add_service(
            self,
            tvm_name: str,
            production_id: int = None,
            testing_id: int = None,
            clown_id: int = None,
            project_id: int = None,
    ) -> perforator_models.Service:
        if tvm_name in self._services:
            raise Conflict
        envs = []
        id_ = next(self._id_generator)
        if production_id:
            envs.append(
                perforator_models.Environment(
                    'production', next(self._env_id_generator), production_id,
                ),
            )
        if testing_id:
            envs.append(
                perforator_models.Environment(
                    'testing', next(self._env_id_generator), testing_id,
                ),
            )
        clown_service = None
        if clown_id and project_id:
            clown_service = perforator_models.ClownService(
                clown_id, project_id,
            )
        service = perforator_models.Service(
            id=id_,
            environments=envs,
            is_internal=bool(clown_service),
            tvm_name=tvm_name,
            clown_service=clown_service,
        )
        self._services[tvm_name] = service
        return service


@pytest.fixture(name='mock_perforator_context')
def _mock_perforator_context() -> MockContext:
    return MockContext()


@pytest.fixture(name='perforator_mockserver')
def _perforator_mockserver(mockserver, mock_perforator_context):
    class Mocks:
        @staticmethod
        @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
        async def _services_retrieve(request):
            body = request.json
            limit = body.get('limit', 25)
            offset = body.get('offset', 0)
            tvm_names = body.get('tvm_names')
            search = body.get('search')
            services = []
            for service in mock_perforator_context.services:
                if offset:
                    offset -= 1
                    continue
                if not limit:
                    break
                search_match = (
                    not search
                    or service.tvm_name == search
                    or search.isdigit()
                    and list(
                        filter(
                            lambda env: (env.tvm_id == int(search)),
                            service.environments,
                        ),
                    )
                )
                tvm_names_match = (
                    not tvm_names or service.tvm_name in tvm_names
                )
                if search_match and tvm_names_match:
                    services.append(service.serialize())
                limit -= 1
            return mockserver.make_response(
                json={'services': services}, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/clowny-perforator/v1.0/services/create')
        async def _services_create(request):
            body = request.json
            production_id = None
            testing_id = None
            for env in body['environments']:
                if env['env_type'] == 'production':
                    production_id = env['tvm_id']
                elif env['env_type'] == 'testing':
                    testing_id = env['tvm_id']
            clown_service = body.get('clown_service')
            clown_id = None
            project_id = None
            if clown_service:
                clown_id = clown_service['clown_id']
                project_id = clown_service['project_id']

            service = mock_perforator_context.add_service(
                body['tvm_name'],
                production_id,
                testing_id,
                clown_id,
                project_id,
            )

            return mockserver.make_response(
                json=service.serialize(), status=200,
            )

        @staticmethod
        @mockserver.json_handler(
            '/clowny-perforator/v1.0/services/rules/retrieve',
        )
        async def _rules_retrieve(request):
            body = request.json
            limit = body.get('limit', 25)
            offset = body.get('offset', 0)
            rules = []
            for rule in mock_perforator_context.rules:
                if offset:
                    offset -= 1
                    continue
                if not limit:
                    break
                rules.append(rule.serialize())
                limit -= 1
            return mockserver.make_response(json={'rules': rules}, status=200)

        @staticmethod
        @mockserver.json_handler(
            '/clowny-perforator/v1.0/services/rules/create',
        )
        async def _rules_create(request):
            body = request.json
            rules = mock_perforator_context.add_rules(
                body['source'], body['destinations'],
            )
            return mockserver.make_response(json=rules.serialize(), status=200)

        @staticmethod
        @mockserver.json_handler(
            '/clowny-perforator/v1.0/services/environments/create',
        )
        async def _environments_create(request):
            body = request.json
            environment = mock_perforator_context.add_environment(
                body['service_id'], body['env_type'], body['tvm_id'],
            )
            return mockserver.make_response(
                json=environment.serialize(), status=200,
            )

        @staticmethod
        @mockserver.json_handler('/clowny-perforator/v1.0/services/edit')
        async def _services_edit(request):
            body = request.json
            service = mock_perforator_context.edit_service(
                body['service_id'],
                perforator_models.ClownService.deserialize(
                    body['clown_service'],
                ),
            )
            return mockserver.make_response(
                json=service.serialize(), status=200,
            )

    return Mocks()
