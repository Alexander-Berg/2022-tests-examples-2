import dataclasses
import typing

import pytest


@dataclasses.dataclass
class Manager:
    taxi_config: typing.Any
    employer_mapping: typing.Dict[str, str] = dataclasses.field(
        default_factory=dict,
    )

    async def add_client(self, *, service_fixture, corp_client_id, employer):
        return await self.add_clients(
            service_fixture=service_fixture,
            clients={corp_client_id: employer},
        )

    async def add_clients(
            self, *, service_fixture, clients: typing.Dict[str, str],
    ):
        self.employer_mapping.update(clients)  # pylint: disable=E1101
        self.taxi_config.set(
            CARGO_CLAIMS_EMPLOYER_NAME_MAPPING=self.employer_mapping,
        )
        await service_fixture.invalidate_caches()


# usage examples:
#
# await cargo_corp_settings.add_client(
#     service_fixture=taxi_united_dispatch,
#     corp_client_id='corp_client_eats_1',
#     employer='eats')
#
# await cargo_corp_settings.add_clients(
#     service_fixture=taxi_united_dispatch,
#     clients={'corp_client_eats_1': 'eats'})
#
@pytest.fixture
def cargo_corp_settings(taxi_config):
    return Manager(taxi_config=taxi_config, employer_mapping={})
