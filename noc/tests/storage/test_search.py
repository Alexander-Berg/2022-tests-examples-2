import ipaddress

import pytest
from hamcrest import assert_that, contains_inanyorder, equal_to, has_length

from ipv4mgr.interface.pool import Net4Type
from ipv4mgr.storage import BaseStorage
from ipv4mgr.storage.errors import PoolNotFoundError
from ipv4mgr.typedefs import Map64JsonDict, MappingDict, PoolDict, YaNetMappingDict

from .utils import convert_first_net

pytestmark = [pytest.mark.asyncio]


async def test_get_pool_id_by_net4_success(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    ip4 = convert_first_net(stateless_pool)[0]
    (net4,) = ipaddress.summarize_address_range(ip4, ip4)
    pool_id = await storage.get_pool_id_by_net4(net4)
    assert pool_id == stateless_pool["id"]


async def test_get_pool_id_by_net4_not_found(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    ip4 = convert_first_net(stateless_pool)[0] - 1
    (net4,) = ipaddress.summarize_address_range(ip4, ip4)
    with pytest.raises(PoolNotFoundError):
        await storage.get_pool_id_by_net4(net4)


async def test_get_pool_id_by_outer_ip4_success(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    ip4 = convert_first_net(stateless_pool)[0]
    db_pool_id = await storage.get_pool_id_by_outer_ip4(ip4)
    assert_that(db_pool_id, equal_to(stateless_pool["id"]))


async def test_get_pool_id_by_outer_ip4_not_found(storage: BaseStorage) -> None:
    with pytest.raises(PoolNotFoundError):
        await storage.get_pool_id_by_outer_ip4(ipaddress.IPv4Address("0.0.0.0"))


async def test_export_to_yanet(
    storage: BaseStorage,
    stateless_mapping: MappingDict,
    stateless_portrange_mapping: MappingDict,
) -> None:
    yanet_export = await storage.export_to_yanet()
    stateless_client_ip6 = stateless_mapping["client_ip6"]
    assert stateless_client_ip6
    stateless_portrange_client_ip6 = stateless_portrange_mapping["client_ip6"]
    assert stateless_portrange_client_ip6
    expected_yanet_export = [
        YaNetMappingDict(
            default=stateless_mapping["default"],
            scheme=Net4Type.STATELESS.value,
            client_ip6=stateless_client_ip6,
            outer_ip4=stateless_mapping["outer_ip4"],
        ),
        YaNetMappingDict(
            default=stateless_portrange_mapping["default"],
            scheme=Net4Type.STATELESS_PORTRANGE.value,
            client_ip6=stateless_portrange_client_ip6,
            outer_ip4=stateless_portrange_mapping["outer_ip4"],
            client_portrange=stateless_portrange_mapping["client_portrange"],
            outer_portrange=stateless_portrange_mapping["outer_portrange"],
        ),
    ]
    assert_that(yanet_export, has_length(len(expected_yanet_export)))
    assert_that(yanet_export, contains_inanyorder(*expected_yanet_export))


async def test_export_map_nat64json(
    storage: BaseStorage,
    stateless_mapping: MappingDict,
    stateless_portrange_mapping: MappingDict,
) -> None:
    map_nat64json = await storage.export_map_nat64json()
    client_ip6 = stateless_mapping["client_ip6"]
    assert client_ip6
    expected_map_nat64json = [
        Map64JsonDict(
            client_ip6=client_ip6,
            outer_ip4=stateless_mapping["outer_ip4"],
            fqdn=stateless_mapping["fqdn"],
            default=stateless_mapping["default"],
        )
    ]
    assert_that(map_nat64json, equal_to(expected_map_nat64json))
