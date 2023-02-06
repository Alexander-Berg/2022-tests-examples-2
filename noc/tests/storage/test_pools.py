import asyncio
import ipaddress
from typing import List

import pytest
from hamcrest import assert_that, equal_to, has_entries, has_length

from ipv4mgr.interface.pool import Net4Info, Net4Type
from ipv4mgr.storage import BaseStorage
from ipv4mgr.storage.errors import (
    CantDeleteNetWithMappingsError,
    Nets4ConflictError,
    PoolAlreadyExistsError,
    PoolNotFoundError,
)
from ipv4mgr.typedefs import AllowDict, MappingDict, Net4Dict, PoolDict

from .utils import (
    convert_first_net,
    convert_net4_dict,
    convert_net4_info,
    convert_pool_dict_to_create_pool_params,
)

pytestmark = [pytest.mark.asyncio]


async def create_pool(
    storage: BaseStorage, pool_id: str, nets4_info_list: List[Net4Info]
) -> PoolDict:
    return await storage.create_pool(
        abc_id=900,
        pool_id=pool_id,
        name="pool name",
        autoreg=False,
        nets4_info_list=nets4_info_list,
        comment="",
        allow_ips6=set(),
        allow_nets6=set(),
        allow_fws=set(),
    )


async def test_create_pool_success(
    storage: BaseStorage, raw_pool_data: PoolDict
) -> None:
    created_pool = await storage.create_pool(
        **convert_pool_dict_to_create_pool_params(raw_pool_data)
    )
    assert_that(created_pool, equal_to(raw_pool_data))
    db_pool = await storage.get_pool(pool_id=raw_pool_data["id"])
    assert created_pool == db_pool


async def test_create_pool_with_already_exists_name(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    with pytest.raises(PoolAlreadyExistsError):
        await storage.create_pool(
            **convert_pool_dict_to_create_pool_params(stateless_pool)
        )


async def test_get_unexistent_pool(storage: BaseStorage) -> None:
    with pytest.raises(PoolNotFoundError):
        await storage.get_pool(pool_id="unexistent_pool_id")


@pytest.mark.parametrize(
    ("net1_str", "net2_str"),
    (
        ("192.168.1.0/32", "192.168.1.0/24"),
        ("192.168.1.0/24", "192.168.1.0/24"),
        ("192.168.1.0/24", "192.168.1.255/32"),
    ),
)
async def test_network_conflicts(
    storage: BaseStorage, net1_str: str, net2_str: str
) -> None:
    net1 = ipaddress.IPv4Network(net1_str)
    net2 = ipaddress.IPv4Network(net2_str)
    assert_that(net1.overlaps(net2))
    with pytest.raises(Nets4ConflictError):
        await asyncio.gather(
            create_pool(
                storage,
                pool_id="pool1",
                nets4_info_list=[Net4Info(net4=net1, type=Net4Type.STATELESS)],
            ),
            create_pool(
                storage,
                pool_id="pool2",
                nets4_info_list=[Net4Info(net4=net2, type=Net4Type.STATELESS)],
            ),
        )


@pytest.mark.parametrize(
    ("net1_str", "net2_str"),
    (("192.168.1.0/24", "192.168.2.0/24"), ("192.168.2.0/24", "192.168.1.0/24")),
)
async def test_network_conflicts_absence_at_adjacent_nets(
    storage: BaseStorage, net1_str: str, net2_str: str
) -> None:
    net1 = ipaddress.IPv4Network(net1_str)
    net2 = ipaddress.IPv4Network(net2_str)
    assert_that(not net1.overlaps(net2))
    await create_pool(
        storage,
        pool_id="pool1",
        nets4_info_list=[Net4Info(net4=net1, type=Net4Type.STATELESS)],
    )
    await create_pool(
        storage,
        pool_id="pool2",
        nets4_info_list=[Net4Info(net4=net2, type=Net4Type.STATELESS)],
    )


async def test_delete_unexistent_pool(storage: BaseStorage) -> None:
    with pytest.raises(PoolNotFoundError):
        await storage.delete_pool(pool_id="unexistent_pool_id")


async def test_recreate_deleted_pool(
    storage: BaseStorage, raw_stateless_pool_data: PoolDict
) -> None:
    await storage.create_pool(
        **convert_pool_dict_to_create_pool_params(raw_stateless_pool_data)
    )
    await storage.delete_pool(pool_id=raw_stateless_pool_data["id"])
    await storage.create_pool(
        **convert_pool_dict_to_create_pool_params(raw_stateless_pool_data)
    )


class TestChangePool:
    async def test_unexistent_pool(self, storage: BaseStorage) -> None:
        with pytest.raises(PoolNotFoundError):
            await storage.change_pool(pool_id="unexistent_pool_id")

    async def test_rewrite_same_net_mapping_not_deleted(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
        stateless_mapping: MappingDict,
    ) -> None:
        await storage.change_pool(
            pool_id=stateless_pool["id"],
            nets4_info_list=[
                convert_net4_dict(net4) for net4 in stateless_pool["nets4"]
            ],
        )
        db_pool = await storage.get_pool(
            pool_id=stateless_pool["id"], add_mappings=True
        )
        assert_that(db_pool, has_entries(PoolDict(nets4=stateless_pool["nets4"])))
        assert_that(db_pool["mappings"], has_length(1))

    async def test_rewrite_same_net_changed_portrange(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
        stateless_mapping: MappingDict,
    ) -> None:
        await storage.change_pool(
            pool_id=stateless_pool["id"],
            nets4_info_list=[
                convert_net4_dict(net4) for net4 in stateless_pool["nets4"]
            ],
        )
        db_pool = await storage.get_pool(
            pool_id=stateless_pool["id"], add_mappings=True
        )
        assert_that(db_pool, has_entries(PoolDict(nets4=stateless_pool["nets4"])))
        assert_that(db_pool["mappings"], has_length(1))

    async def test_rewrite_same_net_changed_portrange_step(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
    ) -> None:

        assert len(stateless_pool["nets4"]) == 1
        net4_dict = stateless_pool["nets4"][0]
        assert net4_dict["type"] == Net4Type.STATELESS.value

        new_net4_info = Net4Info(
            net4=ipaddress.IPv4Network(net4_dict["cidr"]),
            type=Net4Type.STATELESS_PORTRANGE,
            portrange_step=64,
        )

        await storage.change_pool(
            pool_id=stateless_pool["id"],
            nets4_info_list=[new_net4_info],
        )
        db_pool = await storage.get_pool(
            pool_id=stateless_pool["id"], add_mappings=True
        )
        assert_that(
            db_pool, has_entries(PoolDict(nets4=[convert_net4_info(new_net4_info)]))
        )

    async def test_cant_delete_net_with_mapping(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
        stateless_mapping: MappingDict,
    ) -> None:
        assert len(stateless_pool["nets4"]) == 1
        net4_dict = stateless_pool["nets4"][0]
        assert net4_dict["type"] == Net4Type.STATELESS.value

        new_net4_info = Net4Info(
            net4=ipaddress.IPv4Network(net4_dict["cidr"]),
            type=Net4Type.STATELESS_PORTRANGE,
            portrange_step=64,
        )
        with pytest.raises(CantDeleteNetWithMappingsError):
            await storage.change_pool(
                pool_id=stateless_pool["id"],
                nets4_info_list=[new_net4_info],
            )

    async def test_success_delete_net(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
        stateless_mapping: MappingDict,
    ) -> None:
        assert len(stateless_pool["nets4"]) == 1
        net4_dict = stateless_pool["nets4"][0]
        assert net4_dict["type"] == Net4Type.STATELESS.value

        new_net4_info = Net4Info(
            net4=ipaddress.IPv4Network(net4_dict["cidr"]),
            type=Net4Type.STATELESS_PORTRANGE,
            portrange_step=64,
        )
        with pytest.raises(CantDeleteNetWithMappingsError):
            await storage.change_pool(
                pool_id=stateless_pool["id"],
                nets4_info_list=[new_net4_info],
            )

    async def test_success_add_net(
        self,
        storage: BaseStorage,
        stateless_pool: PoolDict,
    ) -> None:
        assert len(stateless_pool["nets4"]) == 1
        existing_net4 = convert_first_net(stateless_pool)
        new_net4 = ipaddress.IPv4Network("192.0.12.0/30")
        assert not existing_net4.overlaps(new_net4)
        new_net4_info = Net4Info(
            net4=new_net4,
            type=Net4Type.STATELESS,
            portrange_step=64,
        )

        await storage.change_pool(
            pool_id=stateless_pool["id"],
            nets4_info_list=[new_net4_info],
        )

    async def test_change_simple_params(self, storage: BaseStorage) -> None:
        pool_id = "test_pool_id"
        raw_pool_data = PoolDict(
            abc_id=123,
            id=pool_id,
            name="stateless pool name",
            autoreg=False,
            nets4=[Net4Dict(cidr="192.169.12.0/30", type=Net4Type.STATELESS.value)],
            comment="stateless pool comment",
            allow=AllowDict(ips6=["::1"], nets6=["1::/96"], fws=["_TEST_MACRO_"]),
        )
        pool = await storage.create_pool(
            **convert_pool_dict_to_create_pool_params(raw_pool_data)
        )
        assert_that(pool, equal_to(raw_pool_data))

        await storage.change_pool(
            pool_id=pool_id,
            autoreg=True,
            allow_ips6={ipaddress.IPv6Address("::2")},
            allow_nets6={ipaddress.IPv6Network("2::/96")},
            allow_fws={"_CHANGED_MACRO_"},
            name="changed name",
            comment="changed comment",
        )

        expected_pool = PoolDict(
            abc_id=123,
            id=pool_id,
            name="changed name",
            autoreg=True,
            nets4=[Net4Dict(cidr="192.169.12.0/30", type=Net4Type.STATELESS.value)],
            comment="changed comment",
            allow=AllowDict(ips6=["::2"], nets6=["2::/96"], fws=["_CHANGED_MACRO_"]),
        )

        db_pool = await storage.get_pool(pool_id)
        assert_that(db_pool, equal_to(expected_pool))


async def test_get_pools_id_name(
    storage: BaseStorage, stateless_pool: PoolDict
) -> None:
    pools_id_name = await storage.get_pools_id_name()
    expected_pools_id_name = [
        PoolDict(id=stateless_pool["id"], name=stateless_pool["name"])
    ]
    assert_that(
        pools_id_name,
        equal_to(expected_pools_id_name),
    )
