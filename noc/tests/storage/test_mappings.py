import asyncio
import functools
import ipaddress
import random
from typing import List, Optional

import pytest
from hamcrest import assert_that, equal_to, has_entries

from ipv4mgr.interface.pool import Net4Type
from ipv4mgr.storage import BaseStorage
from ipv4mgr.storage.errors import (
    IPv4DoesntBelongToPoolError,
    MappingAlreadyExistsError,
    MappingNotFoundError,
    MultipleMappingsMatchError,
    Net4DoesntBelongToPoolError,
    NoAvailableMappingsError,
    PoolNotFoundError,
    ReservedMappingNotFoundError,
)
from ipv4mgr.typedefs import AllowDict, MappingDict, Net4Dict, PoolDict

from .utils import convert_first_net, convert_pool_dict_to_create_pool_params

pytestmark = [pytest.mark.asyncio]


def get_portrange_step(portrange: List[int]) -> int:
    return portrange[1] - portrange[0] + 1


async def test_create_mapping_unexistent_pool(storage: BaseStorage) -> None:
    with pytest.raises(PoolNotFoundError):
        await storage.create_mapping(
            pool_id="unexistent_pool",
            client_ip6=ipaddress.IPv6Address("::1"),
            client_port_begin=0,
            default=False,
            outer_ip4=ipaddress.IPv4Address("222.222.222.222"),
        )


@pytest.mark.parametrize("client_ip6", (ipaddress.IPv6Address("0::"), None))
async def test_create_mappings_already_exists_with_same_outer_ip4(
    storage: BaseStorage,
    stateless_pool: PoolDict,
    client_ip6: Optional[ipaddress.IPv6Address],
) -> None:
    net4 = convert_first_net(stateless_pool)

    await storage.create_mapping(
        pool_id=stateless_pool["id"],
        client_ip6=client_ip6,
        client_port_begin=0,
        default=False,
        outer_ip4=net4[0],
    )

    with pytest.raises(MappingAlreadyExistsError):
        await storage.create_mapping(
            pool_id=stateless_pool["id"],
            client_ip6=client_ip6,
            client_port_begin=0,
            default=False,
            outer_ip4=net4[0],
        )


async def test_create_mappings_ip_not_belongs_to_pool(
    storage: BaseStorage,
    stateless_pool: PoolDict,
) -> None:
    ip4 = ipaddress.IPv4Address("0.0.0.0")
    for raw_net in stateless_pool["nets4"]:
        assert ip4 not in ipaddress.IPv4Network(raw_net["cidr"])

    with pytest.raises(IPv4DoesntBelongToPoolError):
        await storage.create_mapping(
            pool_id=stateless_pool["id"],
            client_ip6=ipaddress.IPv6Address("0::"),
            client_port_begin=0,
            default=False,
            outer_ip4=ip4,
        )


async def test_create_mappings_net4_not_belongs_to_pool(
    storage: BaseStorage,
    stateless_pool: PoolDict,
) -> None:
    net4 = ipaddress.IPv4Network("0.0.0.0/30")
    for raw_net4_info in stateless_pool["nets4"]:
        assert not net4.overlaps(ipaddress.IPv4Network(raw_net4_info["cidr"]))

    with pytest.raises(Net4DoesntBelongToPoolError):
        await storage.create_mapping(
            pool_id=stateless_pool["id"],
            client_ip6=ipaddress.IPv6Address("0::"),
            client_port_begin=0,
            default=False,
            outer_ip4=None,
            outer_net4=net4,
        )


async def test_get_unexistent_mapping(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    with pytest.raises(MappingNotFoundError):
        await storage.get_mapping(pool_id=stateless_pool["id"], mapping_id="0" * 24)


async def test_create_mapping_change_default(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    pool_id = stateless_pool["id"]
    ip6 = ipaddress.IPv6Address("ff::")

    mapping1 = await storage.create_mapping(
        pool_id=pool_id,
        client_ip6=ip6,
        client_port_begin=None,
        default=True,
        outer_ip4=None,
    )
    assert mapping1["default"]

    mapping2 = await storage.create_mapping(
        pool_id=pool_id,
        client_ip6=ip6,
        client_port_begin=None,
        default=True,
        outer_ip4=None,
    )
    assert mapping2["default"]

    db_mapping1 = await storage.get_mapping(pool_id=pool_id, mapping_id=mapping1["id"])
    assert not db_mapping1["default"]
    mapping1["default"] = False
    assert_that(db_mapping1, equal_to(mapping1))

    db_mapping2 = await storage.get_mapping(pool_id=pool_id, mapping_id=mapping2["id"])
    assert db_mapping2["default"]
    assert_that(db_mapping2, equal_to(mapping2))


async def test_client_port_begin_no_available_mappings_in_stateless_pool_error(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    ip4 = convert_first_net(stateless_pool)[0]
    with pytest.raises(NoAvailableMappingsError):
        await storage.create_mapping(
            pool_id=stateless_pool["id"],
            client_port_begin=128,
            client_ip6=None,
            default=False,
            outer_ip4=ip4,
        )


async def test_create_mapping_with_net4(
    storage: BaseStorage,
    stateless_pool: PoolDict,
) -> None:
    ip4 = convert_first_net(stateless_pool)[0]
    (net4,) = ipaddress.summarize_address_range(ip4, ip4)
    mapping = await storage.create_mapping(
        pool_id=stateless_pool["id"],
        client_ip6=ipaddress.IPv6Address("0::"),
        client_port_begin=0,
        default=False,
        outer_ip4=None,
        outer_net4=net4,
    )
    assert mapping["outer_ip4"] == str(ip4)


class TestDeleteMapping:
    async def test_delete_mapping_from_unexistent_pool(
        self, storage: BaseStorage
    ) -> None:
        with pytest.raises(PoolNotFoundError):
            await storage.delete_mapping(
                pool_id="unexistent_id", mapping_id="unexistent_id"
            )

    async def test_delete_unexistent_mapping(
        self, storage: BaseStorage, stateless_pool: PoolDict
    ) -> None:
        with pytest.raises(MappingNotFoundError):
            await storage.delete_mapping(
                pool_id=stateless_pool["id"], mapping_id="0" * 24
            )

    async def test_delete_success(
        self, storage: BaseStorage, stateless_mapping: MappingDict
    ) -> None:
        await storage.delete_mapping(
            pool_id=stateless_mapping["pool_id"], mapping_id=stateless_mapping["id"]
        )
        with pytest.raises(MappingNotFoundError):
            await storage.get_mapping(
                pool_id=stateless_mapping["pool_id"], mapping_id=stateless_mapping["id"]
            )


class TestCreateStatelessPortrangeMapping:
    async def test_create_no_available_mappings_some_ip(
        self, storage: BaseStorage
    ) -> None:
        portrange_step = 1024
        cidr = "192.169.33.255/32"
        raw_pool_data = PoolDict(
            abc_id=123,
            id="test_stateless_portrange_pool_id",
            name="stateless portrange pool name",
            autoreg=False,
            nets4=[
                Net4Dict(
                    cidr=cidr,
                    type=Net4Type.STATELESS_PORTRANGE.value,
                    portrange_step=portrange_step,
                )
            ],
            comment="stateless portrange pool comment",
            allow=AllowDict(ips6=["::1"], nets6=["1::/96"], fws=["_TEST_MACRO_"]),
        )

        pool = await storage.create_pool(
            **convert_pool_dict_to_create_pool_params(raw_pool_data)
        )

        ip_address = next(iter(ipaddress.IPv4Network(cidr)))
        count = 2 ** 16 // portrange_step

        create_mapping = functools.partial(
            storage.create_mapping,
            pool_id=pool["id"],
            client_ip6=ipaddress.IPv6Address("0::"),
            default=True,
            outer_ip4=ip_address,
        )

        mappings_futures = [
            create_mapping(client_port_begin=portrange_step * i) for i in range(count)
        ]
        await asyncio.gather(*mappings_futures)
        with pytest.raises(NoAvailableMappingsError):
            await create_mapping(client_port_begin=0)

    async def test_success(
        self, storage: BaseStorage, stateless_portrange_pool: PoolDict
    ) -> None:
        portrange_step = stateless_portrange_pool["nets4"][0]["portrange_step"]
        assert portrange_step is not None
        outer_ip4 = convert_first_net(stateless_portrange_pool)[0]
        mapping = await storage.create_mapping(
            pool_id=stateless_portrange_pool["id"],
            client_ip6=ipaddress.IPv6Address("::"),
            client_port_begin=portrange_step,
            outer_ip4=outer_ip4,
            default=True,
        )
        expected_mapping_entries = MappingDict(
            client_ip6="::",
            client_portrange=[portrange_step, 2 * portrange_step - 1],
            default=True,
            outer_ip4=str(outer_ip4),
            pool_id=stateless_portrange_pool["id"],
        )
        assert_that(mapping, has_entries(expected_mapping_entries))
        assert get_portrange_step(mapping["client_portrange"]) == portrange_step
        assert get_portrange_step(mapping["outer_portrange"]) == portrange_step


class TestDeleteMappingByNetAndClientIP6:
    async def test_delete_from_unexistent_pool(self, storage: BaseStorage) -> None:
        with pytest.raises(PoolNotFoundError):
            await storage.delete_mapping_by_net_and_client_ip6(
                net4=ipaddress.IPv4Network("192.168.0.0/30"),
                client_ip6=ipaddress.IPv6Address("0::"),
            )

    async def test_delete_unexistent_mapping(
        self, storage: BaseStorage, stateless_pool: PoolDict
    ) -> None:
        with pytest.raises(MappingNotFoundError):
            await storage.delete_mapping_by_net_and_client_ip6(
                net4=convert_first_net(stateless_pool),
                client_ip6=ipaddress.IPv6Address("0::"),
            )

    async def test_delete_success(
        self, storage: BaseStorage, stateless_mapping: MappingDict
    ) -> None:
        pool = await storage.get_pool(stateless_mapping["pool_id"])

        net4 = convert_first_net(pool)
        assert ipaddress.IPv4Address(stateless_mapping["outer_ip4"]) in net4

        db_mapping = await storage.delete_mapping_by_net_and_client_ip6(
            net4=net4,
            client_ip6=ipaddress.IPv6Address(stateless_mapping["client_ip6"]),
        )
        assert db_mapping == stateless_mapping
        with pytest.raises(MappingNotFoundError):
            await storage.get_mapping(
                pool_id=pool["id"], mapping_id=stateless_mapping["id"]
            )

    async def test_delete_multiple_mappings_match_error(
        self, storage: BaseStorage, stateless_pool: PoolDict
    ) -> None:
        net4 = convert_first_net(stateless_pool)
        client_ip6 = ipaddress.IPv6Address("1::")
        for _ in range(2):
            await storage.create_mapping(
                pool_id=stateless_pool["id"],
                client_ip6=client_ip6,
                client_port_begin=0,
                default=False,
                outer_ip4=None,
                outer_net4=net4,
            )

        with pytest.raises(MultipleMappingsMatchError):
            await storage.delete_mapping_by_net_and_client_ip6(
                net4=net4,
                client_ip6=client_ip6,
            )


class TestDeleteMappingByIPs:
    async def test_delete_unexistent_mapping(self, storage: BaseStorage) -> None:
        with pytest.raises(MappingNotFoundError):
            await storage.delete_mapping_by_ips(
                outer_ip4=ipaddress.IPv4Address("127.0.0.1"),
                client_ip6=ipaddress.IPv6Address("0::"),
            )

    async def test_delete_success(
        self, storage: BaseStorage, stateless_mapping: MappingDict
    ) -> None:
        await storage.delete_mapping_by_ips(
            outer_ip4=ipaddress.IPv4Address(stateless_mapping["outer_ip4"]),
            client_ip6=ipaddress.IPv6Address(stateless_mapping["client_ip6"]),
        )


class TestChangeMapping:
    async def test_change_nothing(
        self, storage: BaseStorage, stateless_mapping: MappingDict
    ) -> None:
        await storage.change_mapping(
            pool_id=stateless_mapping["pool_id"],
            mapping_id=stateless_mapping["id"],
            client_ip6=None,
            default=None,
        )
        db_mapping = await storage.get_mapping(
            pool_id=stateless_mapping["pool_id"],
            mapping_id=stateless_mapping["id"],
        )
        assert_that(db_mapping, equal_to(stateless_mapping))

    async def test_change_default(
        self, storage: BaseStorage, stateless_pool: PoolDict
    ) -> None:
        pool_id = stateless_pool["id"]
        ip6 = ipaddress.IPv6Address("ff::")

        mapping1 = await storage.create_mapping(
            pool_id=pool_id,
            client_ip6=ip6,
            client_port_begin=None,
            default=True,
            outer_ip4=None,
        )
        assert mapping1["default"]

        mapping2 = await storage.create_mapping(
            pool_id=pool_id,
            client_ip6=ip6,
            client_port_begin=None,
            default=False,
            outer_ip4=None,
        )
        assert not mapping2["default"]

        db_mapping1 = await storage.get_mapping(
            pool_id=pool_id, mapping_id=mapping1["id"]
        )
        assert db_mapping1["default"]

        await storage.change_mapping(
            pool_id=pool_id, mapping_id=mapping2["id"], default=True
        )

        db_mapping1 = await storage.get_mapping(
            pool_id=pool_id, mapping_id=mapping1["id"]
        )
        assert not db_mapping1["default"]
        mapping1["default"] = False
        assert_that(db_mapping1, equal_to(mapping1))

        db_mapping2 = await storage.get_mapping(
            pool_id=pool_id, mapping_id=mapping2["id"]
        )
        assert db_mapping2["default"]
        mapping2["default"] = True
        assert_that(db_mapping2, equal_to(mapping2))

    async def test_change_client_ip6_reserved_mapping_not_found(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
        stateless_mapping: MappingDict,
    ) -> None:
        new_client_ip6 = str(ipaddress.IPv6Address("1:1:1::"))
        assert new_client_ip6 != stateless_mapping["client_ip6"]
        with pytest.raises(ReservedMappingNotFoundError):
            await storage.change_mapping(
                pool_id=stateless_pool["id"],
                mapping_id=stateless_mapping["id"],
                client_ip6=new_client_ip6,
            )

    async def test_change_client_ip6_success(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
        stateless_mapping: MappingDict,
    ) -> None:
        client_ip6_str = "::"
        pool_id = stateless_pool["id"]
        net4 = list(convert_first_net(stateless_pool))
        mapping = await storage.create_mapping(
            pool_id=pool_id,
            client_ip6=None,
            default=False,
            outer_ip4=random.choice(net4),
            client_port_begin=None,
        )
        mapping_id = mapping["id"]

        await storage.change_mapping(
            pool_id=pool_id,
            mapping_id=mapping_id,
            client_ip6=client_ip6_str,
        )

        mapping["client_ip6"] = client_ip6_str

        db_mapping = await storage.get_mapping(pool_id=pool_id, mapping_id=mapping_id)
        assert_that(db_mapping, equal_to(mapping))
