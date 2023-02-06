import ipaddress
from typing import Dict

from ipv4mgr.interface.pool import Net4Info, Net4Type
from ipv4mgr.typedefs import Net4Dict, PoolDict


def convert_pool_dict_to_create_pool_params(raw_pool: PoolDict) -> Dict:
    allow_params = raw_pool["allow"]
    return {
        "abc_id": raw_pool["abc_id"],
        "pool_id": raw_pool["id"],
        "name": raw_pool["name"],
        "autoreg": raw_pool["autoreg"],
        "nets4_info_list": [convert_net4_dict(net4) for net4 in raw_pool["nets4"]],
        "comment": raw_pool["comment"],
        "allow_ips6": {ipaddress.IPv6Address(ip6) for ip6 in allow_params["ips6"]},
        "allow_nets6": {ipaddress.IPv6Network(net6) for net6 in allow_params["nets6"]},
        "allow_fws": allow_params["fws"],
    }


def convert_first_net(pool_dict: PoolDict) -> ipaddress.IPv4Network:
    return ipaddress.IPv4Network(pool_dict["nets4"][0]["cidr"])


def convert_net4_info(net4_info: Net4Info) -> Net4Dict:
    result = Net4Dict(cidr=str(net4_info.net4), type=net4_info.type.value)
    if net4_info.portrange_step:
        result["portrange_step"] = net4_info.portrange_step
    return result


def convert_net4_dict(net4_dict: Net4Dict) -> Net4Info:
    return Net4Info(
        net4=ipaddress.IPv4Network(net4_dict["cidr"]),
        type=Net4Type(net4_dict["type"]),
        portrange_step=net4_dict.get("portrange_step"),
    )
