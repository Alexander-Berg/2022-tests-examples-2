import pytest

from noc.matilda_clickhouse_proxy.lib import parser
from noc.matilda_clickhouse_proxy.lib import proto_resolv


@pytest.mark.parametrize("query, expected", (
    (
        "NFSENSE BITRATE in_bytes AS rx, out_bytes AS tx",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx, "
        "sum(out_bytes)*8 as tx "
        "FROM tacct_db.tacct_nfsense "
        "GROUP BY t "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE BITRATE RX",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx "
        "FROM tacct_db.tacct_nfsense "
        "GROUP BY t "
        "ORDER BY t, -rx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE BITRATE RX",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx "
        "FROM tacct_db.tacct_nfsense "
        "GROUP BY t "
        "ORDER BY t, -rx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx FROM DB.TABLE",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx "
        "FROM DB.TABLE "
        "GROUP BY t "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE TX",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(out_packets) as tx "
        "FROM tacct_db.tacct_nfsense "
        "GROUP BY t "
        "ORDER BY t, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE BITRATE in_bytes AS rx, out_bytes AS tx FORMAT JSON",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx, "
        "sum(out_bytes)*8 as tx "
        "FROM tacct_db.tacct_nfsense "
        "GROUP BY t "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE BITRATE in_bytes AS rx, out_bytes AS tx TOP BY (), 3",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx, "
        "sum(out_bytes)*8 as tx "
        "FROM tacct_db.tacct_nfsense "
        "GROUP BY t "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE BITRATE in_bytes AS rx, out_bytes AS tx TOP BY dst_geo",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx, "
        "sum(out_bytes)*8 as tx, "
        "dst_geo "
        "FROM tacct_db.tacct_nfsense "
        "WHERE (dst_geo) IN ("
            "SELECT dst_geo FROM tacct_db.tacct_nfsense "
            "GROUP BY dst_geo ORDER BY sum(out_bytes) DESC LIMIT 5"
        ") "
        "GROUP BY t, dst_geo "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx TOP BY 'src_geo'",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx, "
        "src_geo "
        "FROM tacct_db.tacct_nfsense "
        "WHERE (src_geo) IN ("
            "SELECT src_geo FROM tacct_db.tacct_nfsense "
            "GROUP BY src_geo ORDER BY sum(out_packets) DESC LIMIT 5"
        ") "
        "GROUP BY t, src_geo "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx WHERE dst_geo='SAS' FORMAT",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx "
        "FROM tacct_db.tacct_nfsense "
        "WHERE dst_geo='SAS' "
        "GROUP BY t "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx WHERE 1=1 TOP BY src_geo",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx, "
        "src_geo "
        "FROM tacct_db.tacct_nfsense "
        "WHERE 1=1 AND (src_geo) IN ("
            "SELECT src_geo FROM tacct_db.tacct_nfsense "
            "WHERE 1=1 "
            "GROUP BY src_geo ORDER BY sum(out_packets) DESC LIMIT 5"
        ") "
        "GROUP BY t, src_geo "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx WHERE 1=1 TOP BY src_geo,1313",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx, "
        "src_geo "
        "FROM tacct_db.tacct_nfsense "
        "WHERE 1=1 AND (src_geo) IN ("
            "SELECT src_geo FROM tacct_db.tacct_nfsense "
            "WHERE 1=1 "
            "GROUP BY src_geo ORDER BY sum(out_packets) DESC LIMIT 1313"
        ") "
        "GROUP BY t, src_geo "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx WHERE 1=1 TOP BY dict_name[key]",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx, "
        "key as dict_name__key_id, "
        "dictGetString('dict_name', 'name', toUInt64(dict_name__key_id)) as dict_name__key "
        "FROM tacct_db.tacct_nfsense "
        "WHERE 1=1 AND (dict_name__key_id) IN ("
            "SELECT key as dict_name__key_id FROM tacct_db.tacct_nfsense "
            "WHERE 1=1 "
            "GROUP BY dict_name__key_id ORDER BY sum(out_packets) DESC LIMIT 5"
        ") "
        "GROUP BY t, dict_name__key_id "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx WHERE 1=1 TOP BY dict_name[key1;key2], 10",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "key1, key2 as dict_name__key1_key2_id, "
        "dictGetString('dict_name', 'name', toUInt64(dict_name__key1_key2_id)) as dict_name__key1_key2 "
        "FROM tacct_db.tacct_nfsense "
        "WHERE 1=1 AND (dict_name__key1_key2_id) IN ("
            "SELECT key1, key2 as dict_name__key1_key2_id FROM tacct_db.tacct_nfsense "
            "WHERE 1=1 "
            "GROUP BY dict_name__key1_key2_id ORDER BY sum(in_packets) DESC LIMIT 10"
        ") "
        "GROUP BY t, dict_name__key1_key2_id "
        "ORDER BY t, -rx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx WHERE 1=1 TOP BY dict[key1]||dict[key2], 10",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "(key1 != 0 ? key1 : key2) as dict_key1__dict_key2_id, "
        "dictGetString('dict', 'name', toUInt64(dict_key1__dict_key2_id)) as dict_key1__dict_key2 "
        "FROM tacct_db.tacct_nfsense "
        "WHERE 1=1 AND (dict_key1__dict_key2_id) IN ("
            "SELECT (key1 != 0 ? key1 : key2) as dict_key1__dict_key2_id "
            "FROM tacct_db.tacct_nfsense "
            "WHERE 1=1 "
            "GROUP BY dict_key1__dict_key2_id ORDER BY sum(in_packets) DESC LIMIT 10"
        ") "
        "GROUP BY t, dict_key1__dict_key2_id "
        "ORDER BY t, -rx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE TX FROM tacct_db.tacct_nfsense WHERE dst_macro_id IN(SELECT id FROM macro_group WHERE name IN ((ANY))) AND dst_geo IN((ANY))",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(out_packets) as tx "
        "FROM tacct_db.tacct_nfsense "
        "WHERE dst_macro_id IN(SELECT id FROM macro_group WHERE 1) AND 1 "
        "GROUP BY t "
        "ORDER BY t, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE BITRATE in_bytes AS rx, out_bytes AS tx TOP BY src_geo, dst_geo",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_bytes)*8 as rx, "
        "sum(out_bytes)*8 as tx, "
        "src_geo, "
        "dst_geo "
        "FROM tacct_db.tacct_nfsense "
        "WHERE "
        "(src_geo, dst_geo) IN ("
            "SELECT src_geo, dst_geo FROM tacct_db.tacct_nfsense "
            "GROUP BY src_geo, dst_geo ORDER BY sum(out_bytes) DESC LIMIT 5"
        ") "
        "GROUP BY t, src_geo, dst_geo "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE PACKETRATE in_packets as rx, out_packets as tx WHERE 1=1 TOP BY dict_name[key], dict_name_2[key_2]",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "sum(in_packets) as rx, "
        "sum(out_packets) as tx, "
        "key as dict_name__key_id, "
        "key_2 as dict_name_2__key_2_id, "
        "dictGetString('dict_name', 'name', toUInt64(dict_name__key_id)) as dict_name__key, "
        "dictGetString('dict_name_2', 'name', toUInt64(dict_name_2__key_2_id)) as dict_name_2__key_2 "
        "FROM tacct_db.tacct_nfsense "
        "WHERE 1=1 "
        "AND "
        "(dict_name__key_id, dict_name_2__key_2_id) IN ("
            "SELECT "
            "key as dict_name__key_id, "
            "key_2 as dict_name_2__key_2_id "
            "FROM tacct_db.tacct_nfsense "
            "WHERE 1=1 "
            "GROUP BY dict_name__key_id, dict_name_2__key_2_id "
            "ORDER BY sum(out_packets) DESC LIMIT 5"
        ") "
        "GROUP BY t, dict_name__key_id, dict_name_2__key_2_id "
        "ORDER BY t, -rx, -tx "
        "FORMAT JSON"
    ),
    (
        "NFSENSE AGENT avg(conntrack_count) AS conntrack_count, avg(conntrack_max) AS conntrack_max WHERE agent IN((ANY))",

        "SELECT "
        "(intDiv(toUInt32(ts), 30) * 30) * 1000 as t, "
        "avg(conntrack_count) AS conntrack_count, "
        "avg(conntrack_max) AS conntrack_max "
        "FROM tacct_db.tacct_agent "
        "WHERE 1 "
        "GROUP BY t "
        "ORDER BY t "
        "FORMAT JSON"
    ),
    (
        "NFSENSE SELECT 1 FROM DB.TABLE WHERE 1",

        "SELECT 1 FROM DB.TABLE WHERE 1 FORMAT JSON"
    ),
    (
        "NFSENSE SELECT 1 as c FROM DB.TABLE WHERE 1 TOP BY k",

        "SELECT 1 as c, k FROM DB.TABLE WHERE 1 AND "
        "(k) IN (SELECT k FROM DB.TABLE WHERE 1 GROUP BY k ORDER BY 1 as c DESC LIMIT 5) "
        "GROUP BY k "
        "FORMAT JSON"
    ),
    (
        "NFSENSE SELECT count(*) AS C FROM system.parts TOP BY table",
        "SELECT count(*) AS C, table FROM system.parts "
        "WHERE (table) IN (SELECT table FROM system.parts GROUP BY table ORDER BY count(*) AS C DESC LIMIT 5) "
        "GROUP BY table FORMAT JSON"
    ),
    (
        "SELECT DISTINCT dictGetString('agents', 'name', toUInt64(agent_id)) FROM tacct_db.tacct_sflow WHERE ts > now() - 1800",
        "SELECT DISTINCT dictGetString('agents', 'name', toUInt64(agent_id)) FROM tacct_db.tacct_sflow WHERE ts > now() - 1800"
    ),
))
def test_format_proxy(query, expected):
    result = parser.format_query(query)
    assert expected == result


@pytest.mark.parametrize("where_clause, expected", (
    (
        "WHERE (src_geo =~ 'not /.*/')",
        "WHERE (not match(src_geo, '.*'))"
    ),
    (
        "WHERE (src_geo =~ 'SAS', 'VLA')",
        "WHERE (src_geo IN ('SAS', 'VLA'))"
    ),
    (
        "WHERE dst_geo=~/.*SAS/ AND (src_geo =~ '/.*/')",
        "WHERE match(dst_geo, '.*SAS') AND (1)"
    ),
    (
        "WHERE host =~ 'host1' AND (src_geo =~ '/.*/')",
        "WHERE host IN ('host1') AND (1)"
    ),
    (
        "WHERE host =~ 'host1','host2', 'host3' AND (src_geo =~ '/.*/')",
        "WHERE host IN ('host1','host2', 'host3') AND (1)"
    ),
    (
        "WHERE host =~ 'host2.yndx.net' AND (src_geo =~ '/.*/')",
        "WHERE host IN ('host2.yndx.net') AND (1)"
    ),
    (
        "WHERE GIDMATCH(src_geoid_group, tacct_db.geoid, 'SAS','VLA')",
        "WHERE src_geoid_group IN("
        "SELECT group_id FROM tacct_db.geoid_map WHERE id IN("
        "SELECT id FROM tacct_db.geoid WHERE name IN ('SAS','VLA')"
        ")"
        ")"
    ),
    (
        "WHERE GIDMATCH(dst_macro_group, tacct_db.macro, '/SEARCH/')",
        "WHERE dst_macro_group IN("
        "SELECT group_id FROM tacct_db.macro_map WHERE id IN("
        "SELECT id FROM tacct_db.macro WHERE match(name, 'SEARCH')"
        ")"
        ")"
    ),
    (
        "WHERE GIDMATCH(dst_pmacro_group||dst_macro_group, tacct_db.macro, '/SEARCH/')",
        "WHERE (dst_pmacro_group != 0 ? dst_pmacro_group : dst_macro_group) IN("
        "SELECT group_id FROM tacct_db.macro_map WHERE id IN("
        "SELECT id FROM tacct_db.macro WHERE match(name, 'SEARCH')"
        ")"
        ")"
    ),
    (
        "WHERE GIDMATCH(src_macro_group, tacct_db.macro, /.*/) AND "
        "GIDMATCH(dst_macro_group, tacct_db.macro, '/.*/')",

        "WHERE 1 AND 1"
    ),
    (
        "WHERE IDMATCH(src_walle_prj, tacct_db.src_walle_prj, '/.*/') AND "
        "IDMATCH(dst_walle_prj, tacct_db.src_walle_prj, '/.*/')",

        "WHERE 1 AND 1"
    ),
    (
        "WHERE (src_geo =~   '/.*/')",
        "WHERE (1)"
    ),
    (
        "WHERE GIDMATCH(dst_macro_group, tacct_db.macro, 'not /SEARCH/')",
        "WHERE not dst_macro_group IN("
        "SELECT group_id FROM tacct_db.macro_map WHERE id IN("
        "SELECT id FROM tacct_db.macro WHERE match(name, 'SEARCH')"
        ")"
        ")"
    ),
    (
        "WHERE GIDMATCH(dst_pmacro_group||dst_macro_group, tacct_db.macro, 'not /SEARCH/')",
        "WHERE not (dst_pmacro_group != 0 ? dst_pmacro_group : dst_macro_group) IN("
        "SELECT group_id FROM tacct_db.macro_map WHERE id IN("
        "SELECT id FROM tacct_db.macro WHERE match(name, 'SEARCH')"
        ")"
        ")"
    ),
    (
        "WHERE GIDMATCH(src_conductor_group, tacct_db.conductor, '/matilda/') AND "
        "GIDMATCH(dst_conductor_group, tacct_db.conductor, '/matilda/')",
        "WHERE src_conductor_group IN("
        "SELECT group_id FROM tacct_db.conductor_map WHERE id IN("
        "SELECT id FROM tacct_db.conductor WHERE match(name, 'matilda')"
        ")"
        ") AND "
        "dst_conductor_group IN("
        "SELECT group_id FROM tacct_db.conductor_map WHERE id IN("
        "SELECT id FROM tacct_db.conductor WHERE match(name, 'matilda')"
        ")"
        ")"
    ),
    (
        "WHERE IDMATCH(src_walle_prj, tacct_db.src_walle_prj, '/rtc-mtn/') AND "
        "IDMATCH(dst_walle_prj, tacct_db.src_walle_prj, '/rtc-mtn/')",
        "WHERE src_walle_prj IN("
        "SELECT id FROM tacct_db.src_walle_prj WHERE match(name, 'rtc-mtn')"
        ") AND "
        "dst_walle_prj IN("
        "SELECT id FROM tacct_db.src_walle_prj WHERE match(name, 'rtc-mtn')"
        ")"
    ),
    (
        "WHERE IDMATCH(src_walle_prj, tacct_db.src_walle_prj, '/rtc-mtn/') AND "
        "GIDMATCH(dst_conductor_group, tacct_db.conductor, '/matilda/')",
        "WHERE src_walle_prj IN("
        "SELECT id FROM tacct_db.src_walle_prj WHERE match(name, 'rtc-mtn')"
        ") AND "
        "dst_conductor_group IN("
        "SELECT group_id FROM tacct_db.conductor_map WHERE id IN("
        "SELECT id FROM tacct_db.conductor WHERE match(name, 'matilda')"
        ")"
        ")"
    ),
))
def test_where_clause_format(where_clause, expected):
    result = parser._where_clause_format(where_clause)
    assert expected == result


@pytest.mark.parametrize("key, data, result", (
    (
        "dst_geo",
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "rx",
                    "type": "Float64"
                },
                {
                    "name": "tx",
                    "type": "Float64"
                },
                {
                    "name": "dst_geo",
                    "type": "String"
                }
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "rx": 1.5,
                    "tx": 1.5,
                    "dst_geo": "GEO_A"
                },
                {
                    "t": "1517564670000",
                    "rx": 1,
                    "tx": 1,
                    "dst_geo": "GEO_B"
                },
            ],
            "rows": 2,
            "statistics": {},
        },
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "rx_GEO_A",
                    "type": "Float64"
                },
                {
                    "name": "tx_GEO_A",
                    "type": "Float64"
                },
                {
                    "name": "rx_GEO_B",
                    "type": "Float64"
                },
                {
                    "name": "tx_GEO_B",
                    "type": "Float64"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "rx_GEO_A": 1.5,
                    "tx_GEO_A": 1.5,
                    "rx_GEO_B": 1,
                    "tx_GEO_B": 1,
                },
            ],
            "rows": 1,
            "statistics": {},
        },
    ),
    (
        ("src_geo", "dst_geo"),
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "rx",
                    "type": "Float64"
                },
                {
                    "name": "tx",
                    "type": "Float64"
                },
                {
                    "name": "src_geo",
                    "type": "String"
                },
                {
                    "name": "dst_geo",
                    "type": "String"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "rx": 1.5,
                    "tx": 1.5,
                    "src_geo": "GEO_A",
                    "dst_geo": "GEO_B",
                },
                {
                    "t": "1517564670000",
                    "rx": 1,
                    "tx": 1,
                    "src_geo": "GEO_B",
                    "dst_geo": "GEO_B",
                },
            ],
            "rows": 2,
            "statistics": {},
        },
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "rx_GEO_A_GEO_B",
                    "type": "Float64"
                },
                {
                    "name": "tx_GEO_A_GEO_B",
                    "type": "Float64"
                },
                {
                    "name": "rx_GEO_B",
                    "type": "Float64"
                },
                {
                    "name": "tx_GEO_B",
                    "type": "Float64"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "rx_GEO_A_GEO_B": 1.5,
                    "tx_GEO_A_GEO_B": 1.5,
                    "rx_GEO_B": 1,
                    "tx_GEO_B": 1,
                },
            ],
            "rows": 1,
            "statistics": {},
        },
    ),
    (
        ("proto", "server_port"),
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "rx",
                    "type": "Float64"
                },
                {
                    "name": "tx",
                    "type": "Float64"
                },
                {
                    "name": "proto",
                    "type": "UInt8"
                },
                {
                    "name": "server_port",
                    "type": "UInt16"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "rx": 1.5,
                    "tx": 1.5,
                    "proto": 17,
                    "server_port": 53,
                },
                {
                    "t": "1517564670000",
                    "rx": 1,
                    "tx": 1,
                    "proto": 6,
                    "server_port": 443,
                },
            ],
            "rows": 2,
            "statistics": {},
        },
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "rx_udp_domain",
                    "type": "Float64"
                },
                {
                    "name": "tx_udp_domain",
                    "type": "Float64"
                },
                {
                    "name": "rx_tcp_https",
                    "type": "Float64"
                },
                {
                    "name": "tx_tcp_https",
                    "type": "Float64"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "rx_udp_domain": 1.5,
                    "tx_udp_domain": 1.5,
                    "rx_tcp_https": 1,
                    "tx_tcp_https": 1,
                },
            ],
            "rows": 1,
            "statistics": {},
        },
    ),
    (
        ("src_geo", "dst_geo"),
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "_",
                    "type": "Float64"
                },
                {
                    "name": "src_geo",
                    "type": "String"
                },
                {
                    "name": "dst_geo",
                    "type": "String"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "_": 1.5,
                    "src_geo": "GEO_A",
                    "dst_geo": "GEO_B",
                },
                {
                    "t": "1517564670000",
                    "_": 1,
                    "src_geo": "GEO_B",
                    "dst_geo": "GEO_B",
                },
            ],
            "rows": 2,
            "statistics": {},
        },
        {
            "meta":
            [
                {
                    "name": "t",
                    "type": "UInt64"
                },
                {
                    "name": "GEO_A_GEO_B",
                    "type": "Float64"
                },
                {
                    "name": "GEO_B",
                    "type": "Float64"
                },
            ],
            "data":
            [
                {
                    "t": "1517564670000",
                    "GEO_A_GEO_B": 1.5,
                    "GEO_B": 1,
                },
            ],
            "rows": 1,
            "statistics": {},
        },
    ),
))
def test_top_by_mutate(key, data, result):
    mutated_data = parser._top_by_mutate(key, data)
    assert mutated_data == result


@pytest.mark.parametrize("data, result", (
    (
        [
            {
                "t": "1000",
                "tx": 1.0,
                "rx": 1.0,
            },
        ],
        [
        ],
    ),
    (
        [
            {
                "t": "1000",
                "tx": 1.0,
                "rx": 1.0,
            },
            {
                "t": "2000",
                "tx": 1.0,
                "rx": 1.0,
            },
            {
                "t": "5000",
                "tx": 3.0,
                "rx": 3.0,
            },
        ],
        [
            {
                "t": "2000",
                "tx": 1.0,
                "rx": 1.0,
            },
            {
                "t": "5000",
                "tx": 1.0,
                "rx": 1.0,
            },
        ],
    ),
))
def test_rate_mutate(data, result):
    data = {"data": data}
    mutated_data = parser._rate_mutate(data)["data"]
    assert mutated_data == result


@pytest.mark.parametrize("query, where_clause", (
    (
        "SELECT pageURL, pageRank FROM rankings_1node WHERE pageRank > 1000",
        "WHERE pageRank > 1000"
    ),
    (
        "SELECT cab_type, count(*) FROM trips_mergetree GROUP BY cab_type",
        ""
    ),
    (
        "SELECT Carrier, avg(DepDelay > 10) * 1000 AS c3 FROM ontime WHERE Year = 2007 GROUP BY Carrier ORDER BY Carrier",
        "WHERE Year = 2007"
    ),
))
def test_get_where_clause_ch(query, where_clause):
    found_clause = parser._get_where_clause_ch(query)
    assert found_clause == where_clause


@pytest.mark.parametrize("query, where_clause", (
    (
        "NFSENSE BITRATE TOP BY dst_macro WHERE 1=1",
        "WHERE 1=1"
    ),
    (
        "NFSENSE PACKETRATE TOP BY src_geo",
        ""
    ),
    (
        "NFSENSE PACKETRATE WHERE 1=2 TOP BY src_geo",
        "WHERE 1=2"
    ),
))
def test_get_where_clause_nf(query, where_clause):
    found_clause = parser._get_where_clause_nf(query)
    assert found_clause == where_clause


@pytest.mark.parametrize("where_clause, ts_col_name, cur_epoch, exp_range_secs", (
    (
        "WHERE 1=1", "ts", 0,
        0
    ),
    (
        "WHERE ts BETWEEN toDateTime(0) AND toDateTime(1234)", "ts", 0,
        1234
    ),
    (
        "WHERE t BETWEEN 20 AND 10", "t", 0,
        10
    ),
    (
        "WHERE t > toDateTime(1000)", "t", 1234,
        234
    ),
    (
        "WHERE t >= toDateTime(1000)", "t", 1234,
        234
    ),
    (
        "WHERE ts > 5000", "ts", 5678,
        678
    ),
    (
        "WHERE ts > 5000", "ts", 1,
        0
    ),
))
def test_get_ts_range_secs(where_clause, ts_col_name, cur_epoch, exp_range_secs):
    range_secs = parser._get_ts_range_secs(where_clause, ts_col_name, cur_epoch)
    assert range_secs == exp_range_secs


@pytest.mark.parametrize("query, exp_quant", (
    (
        "NFSENSE SELECT a",
        30
    ),
    (
        "NFSENSE SELECT a QUANTUM 60",
        60
    ),
    (
        "NFSENSE SELECT ts, a WHERE ts BETWEEN 100 AND 200 POINTS 10",
        30
    ),
    (
        "NFSENSE SELECT ts, a WHERE ts BETWEEN 100 AND 700 POINTS 10",
        90
    ),
    (
        "NFSENSE SELECT ts, a WHERE ts BETWEEN 0 AND 1222 POINTS 10",
        150
    ),
    (
        "NFSENSE SELECT ts, a WHERE ts POINTS 10 QUANTUM 30",
        30
    ),
))
def test_get_quantum(query, exp_quant):
    quant = parser._get_quantum(query, 30)
    assert quant == exp_quant


@pytest.mark.parametrize("query, exp_hints", (
    ("NFSENSE SELECT ts, a WHERE ts POINTS 10 QUANTUM 30 -- HINTS NOAGG 1",
     {parser.QueryHints.NOAGG: True}),
    (("NFSENSE SELECT ts, a WHERE ts POINTS 10 QUANTUM 30 -- HINTS NOAGG 1"
      "\n--HINTS NOAGG 0\n--HINTS DATASOURCE MdB"),
     {parser.QueryHints.NOAGG: False, parser.QueryHints.DATASOURCE: "mdb"}),
    ("NFSENSE SELECT ts, a WHERE ts POINTS 10 QUANTUM 30 -- HINTS NOAGG 1 DATASOURCE mdb",
     {parser.QueryHints.NOAGG: True, parser.QueryHints.DATASOURCE: "mdb"}),
))
def test_get_hints(query, exp_hints):
    hints = parser.get_query_hints(query)
    assert hints == exp_hints


@pytest.mark.parametrize("proto_num, proto_name", (
    (0, "ip"),
    (-1, "-1"),
    (41, "ipv6"),
))
def test_resolv_proto_name(proto_num, proto_name):
    result_proto_name = proto_resolv.resolv_proto_name(proto_num)
    assert result_proto_name == proto_name


@pytest.mark.parametrize("port_num, port_name", (
    (-1, "-1"),
    (80, "http"),
    (443, "https"),
))
def test_resolv_port_name(port_num, port_name):
    result_port_name = proto_resolv.resolv_port_name(port_num)
    assert result_port_name == port_name
