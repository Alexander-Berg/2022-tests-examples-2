import asyncio
import ipaddress
import logging
import random
from asyncio import AbstractEventLoop
from typing import Any, AsyncGenerator, Generator, List

import pytest
from _pytest.fixtures import SubRequest
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors

from ipv4mgr.interface.pool import Net4Type
from ipv4mgr.settings import MongoSettings, ZookeeperSettings
from ipv4mgr.storage import BaseStorage, Storage
from ipv4mgr.typedefs import AllowDict, MappingDict, Net4Dict, PoolDict

from .utils import convert_first_net, convert_pool_dict_to_create_pool_params

logger = logging.getLogger(__name__)


# NOTE: Prevent ScopeMismatch error
@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def mongo_urls() -> List[str]:
    return ["localhost:27011", "localhost:27012", "localhost:27013"]


@pytest.fixture(scope="session")
async def replicaset_init(mongo_urls: List[str]) -> None:
    clients = [
        AsyncIOMotorClient(host=f"mongodb://{host}", connect=True)
        for host in mongo_urls
    ]
    # Await until all mongo hosts are started.
    tasks = [client.admin.command("ping") for client in clients]
    await asyncio.gather(*tasks)

    # NOTE: try-except is hack to run on MacOS, that doesn't support network_mode: host
    try:
        result = await clients[0].admin.command(
            "replSetInitiate",
            {
                "_id": "rs0",
                "members": [
                    {"_id": i, "host": host} for i, host in enumerate(mongo_urls)
                ],
            },
        )
    except errors.OperationFailure as e:
        if e.details and e.details.get("codeName") == "AlreadyInitialized":
            return
        logger.exception(e)
        raise
    logger.info(result)


@pytest.fixture(scope="session")
def mongo_settings(mongo_urls: List[str]) -> MongoSettings:
    return MongoSettings(
        url=f"mongodb://{','.join(mongo_urls)}/?replicaSet=rs0",
        user="",
        passwd="",
    )


@pytest.fixture(scope="session")
async def storage(
    replicaset_init: Any, mongo_settings: MongoSettings
) -> AsyncGenerator[BaseStorage, None]:
    storage = Storage(
        mongo_settings=mongo_settings,
        zookeeper_settings=ZookeeperSettings(
            nodes=("localhost:2181", "localhost:2182", "localhost:2183"),
            timeout=10.0,
            chroot="/ipv4mgr",
        ),
    )
    await storage.init()
    yield storage
    await storage.close()


@pytest.fixture
async def mongo_replicaset_client(mongo_settings: MongoSettings) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(host=mongo_settings.url, w="majority")


@pytest.fixture(autouse=True)
async def truncate_tables(mongo_replicaset_client: AsyncIOMotorClient) -> None:
    await asyncio.gather(
        mongo_replicaset_client["ipv4mgr"]["pools"].delete_many(filter={}),
        mongo_replicaset_client["ipv4mgr"]["nets4"].delete_many(filter={}),
        mongo_replicaset_client["ipv4mgr"]["mappings"].delete_many(filter={}),
    )


@pytest.fixture
def raw_stateless_pool_data() -> PoolDict:
    return PoolDict(
        abc_id=123,
        id="test_stateless_pool_id",
        name="stateless pool name",
        autoreg=False,
        nets4=[Net4Dict(cidr="192.169.12.0/30", type=Net4Type.STATELESS.value)],
        comment="stateless pool comment",
        allow=AllowDict(ips6=["::1"], nets6=["1::/96"], fws=["_TEST_MACRO_"]),
    )


@pytest.fixture
def raw_stateless_portrange_pool_data() -> PoolDict:
    return PoolDict(
        abc_id=123,
        id="test_stateless_portrange_pool_id",
        name="stateless portrange pool name",
        autoreg=False,
        nets4=[
            Net4Dict(
                cidr="192.169.33.0/30",
                type=Net4Type.STATELESS_PORTRANGE.value,
                portrange_step=64,
            )
        ],
        comment="stateless portrange pool comment",
        allow=AllowDict(ips6=["::1"], nets6=["1::/96"], fws=["_TEST_MACRO_"]),
    )


# NOTE: https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html
@pytest.fixture(params=["raw_stateless_pool_data", "raw_stateless_portrange_pool_data"])
def raw_pool_data(request: SubRequest) -> None:
    return request.getfixturevalue(request.param)


@pytest.fixture
async def stateless_pool(
    storage: BaseStorage, raw_stateless_pool_data: PoolDict
) -> PoolDict:
    return await storage.create_pool(
        **convert_pool_dict_to_create_pool_params(raw_stateless_pool_data)
    )


@pytest.fixture
async def stateless_mapping_data(stateless_pool: PoolDict) -> MappingDict:
    net4 = list(convert_first_net(stateless_pool))
    return MappingDict(
        client_ip6="0::",
        default=False,
        outer_ip4=str(random.choice(net4)),
        fqdn="fqdn",
    )


@pytest.fixture
async def stateless_mapping(
    storage: BaseStorage, stateless_pool: PoolDict, stateless_mapping_data: MappingDict
) -> MappingDict:
    return await storage.create_mapping(
        pool_id=stateless_pool["id"],
        client_ip6=ipaddress.IPv6Address(stateless_mapping_data["client_ip6"]),
        client_port_begin=None,
        default=stateless_mapping_data["default"],
        outer_ip4=ipaddress.IPv4Address(stateless_mapping_data["outer_ip4"]),
        fqdn=stateless_mapping_data["fqdn"],
    )


@pytest.fixture
async def stateless_portrange_pool(
    storage: BaseStorage, raw_stateless_portrange_pool_data: PoolDict
) -> PoolDict:
    return await storage.create_pool(
        **convert_pool_dict_to_create_pool_params(raw_stateless_portrange_pool_data)
    )


@pytest.fixture
async def stateless_portrange_mapping_data(
    stateless_portrange_pool: PoolDict,
) -> MappingDict:
    first_net4_dict = stateless_portrange_pool["nets4"][0]

    ip_addresses = list(ipaddress.IPv4Network(first_net4_dict["cidr"]))
    portrange_step = first_net4_dict["portrange_step"]
    assert portrange_step
    return MappingDict(
        client_ip6="0::",
        default=False,
        outer_ip4=str(random.choice(ip_addresses)),
        client_portrange=[portrange_step, 2 * portrange_step],
        fqdn="fqdn",
    )


@pytest.fixture
async def stateless_portrange_mapping(
    storage: BaseStorage,
    stateless_portrange_pool: PoolDict,
    stateless_portrange_mapping_data: MappingDict,
) -> MappingDict:
    return await storage.create_mapping(
        pool_id=stateless_portrange_pool["id"],
        client_ip6=ipaddress.IPv6Address(
            stateless_portrange_mapping_data["client_ip6"]
        ),
        client_port_begin=stateless_portrange_mapping_data["client_portrange"][0],
        default=stateless_portrange_mapping_data["default"],
        outer_ip4=ipaddress.IPv4Address(stateless_portrange_mapping_data["outer_ip4"]),
        fqdn=stateless_portrange_mapping_data["fqdn"],
    )
