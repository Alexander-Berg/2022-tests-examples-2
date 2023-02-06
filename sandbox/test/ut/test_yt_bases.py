import pytest

from sandbox.projects.common.yabs.server.db.yt_bases import (
    skip_node_by_attributes,
    CS_IMPORT_VER_ATTR,
    BIN_DBS_NAMES_ATTR,
    IS_REUSABLE_ATTR,
    IMPORTERS_ATTR,
)


class TestFindNodeToReuse(object):
    @pytest.mark.parametrize(
        ("filter_attributes", "node_attributes", "expected"),
        [
            ({},
             {},
             True),
            ({},
             {IS_REUSABLE_ATTR: False},
             True),
            ({},
             {IS_REUSABLE_ATTR: 'true'},
             True),
            ({},
             {IS_REUSABLE_ATTR: 'false'},
             True),
            ({},
             {IS_REUSABLE_ATTR: True},
             False),
        ]
    )
    def test_skip_node_by_attributes_is_reusable(self, filter_attributes, node_attributes, expected):
        assert skip_node_by_attributes(filter_attributes, node_attributes) == expected

    @pytest.mark.parametrize(
        ("filter_attributes", "node_attributes", "expected"),
        [
            ({CS_IMPORT_VER_ATTR: "123"},
             {CS_IMPORT_VER_ATTR: ["123"]},
             False),
            ({CS_IMPORT_VER_ATTR: "123"},
             {CS_IMPORT_VER_ATTR: ["123", "234"]},
             False),
            ({CS_IMPORT_VER_ATTR: "123"},
             {CS_IMPORT_VER_ATTR: ["234"]},
             True),
        ]
    )
    def test_skip_node_by_attributes_cs_import_ver(self, filter_attributes, node_attributes, expected):
        node_attributes.update({IS_REUSABLE_ATTR: True})
        assert skip_node_by_attributes(filter_attributes, node_attributes) == expected

    @pytest.mark.parametrize(
        ("filter_attributes", "node_attributes", "expected"),
        [
            ({BIN_DBS_NAMES_ATTR: ["st125"]},
             {BIN_DBS_NAMES_ATTR: ["st125", "st124"]},
             False),
            ({BIN_DBS_NAMES_ATTR: ["st001", "st002"]},
             {BIN_DBS_NAMES_ATTR: ["st001", "st003"]},
             True),
        ]
    )
    def test_skip_node_by_attributes_bin_db_names(self, filter_attributes, node_attributes, expected):
        node_attributes.update({IS_REUSABLE_ATTR: True})
        assert skip_node_by_attributes(filter_attributes, node_attributes) == expected

    @pytest.mark.parametrize(
        ('filter_importer_attributes', 'node_importer_attributes', 'expected'),
        [
            (
                {'importer1': {}},
                {'importer1': {'hello': 'world'}},
                False
            ),
            (
                {'importer1': {}},
                {'importer1': {}},
                False
            ),
            (
                {'importer1': {'hello': 'world'}},
                {'importer1': {'hello': 'world'}},
                False
            ),
            (
                {'importer1': {'hello': 'world', 'foo': 'bar'}},
                {'importer1': {'hello': 'world', 'foo': 'bar'}},
                False
            ),
            (
                {'importer1': {'hello': 'world'}},
                {'importer1': {'hello': 'world', 'foo': 'bar'}},
                False
            ),
            (
                {'importer1': {'hello': 'world', 'foo': 'bar'}},
                {'importer1': {'hello': 'world'}},
                True
            ),
            (
                {'importer1': {'hello': 'world', 'foo': 'bar'}},
                {'importer1': {'hello': 'hell'}},
                True
            ),
            (
                {'importer1': {'hello': 'world', 'foo': 'bar'}},
                {'importer1': {}},
                True
            ),
            (
                {'importer1': {}},
                {'importer1': {'hello': 'world'}, 'importer2': {'foo': 'bar'}},
                False
            ),
            (
                {'importer1': {'hello': 'world'}},
                {'importer1': {'hello': 'world'}, 'importer2': {'foo': 'bar'}},
                False
            ),
            (
                {'importer2': {'foo': 'bar'}},
                {'importer1': {'hello': 'world'}, 'importer2': {'foo': 'bar'}},
                False
            ),
            (
                {'importer3': {'foo': 'bar'}},
                {'importer1': {'hello': 'world'}, 'importer2': {'foo': 'bar'}},
                True
            ),
        ]
    )
    def test_skip_node_by_importer_attributes(self, filter_importer_attributes, node_importer_attributes, expected):
        filter_attributes = {
            IMPORTERS_ATTR: filter_importer_attributes
        }
        node_attributes = {
            IMPORTERS_ATTR: node_importer_attributes,
            IS_REUSABLE_ATTR: True,
        }
        assert skip_node_by_attributes(filter_attributes, node_attributes) == expected

    @pytest.mark.parametrize(
        ("filter_attributes", "node_attributes", "expected"),
        [
            ({"my_attribute": "my_value"},
             {"my_attribute": "my_value"},
             False),
            ({"my_attribute": "my_value"},
             {"my_attribute": "my_other_value"},
             True),
            ({"my_attribute": "my_value"},
             {"my_attribute": "my_value",
              "my_other_attribute": "my_other_value"},
             False),
            ({"my_attribute": "my_value",
              "my_other_attribute": "my_other_value"},
             {"my_attribute": "my_value"},
             True),
            ({"my_attribute": None},
             {},
             True),
            ({"my_attribute": "my_value"},
             {},
             True),
        ]
    )
    def test_skip_node_by_attributes_any_other_attribute(self, filter_attributes, node_attributes, expected):
        node_attributes.update({IS_REUSABLE_ATTR: True})
        assert skip_node_by_attributes(filter_attributes, node_attributes) == expected

    @pytest.mark.parametrize(
        ("filter_attributes", "node_attributes", "expected"),
        [
            (
                {
                    "__settings_spec_md5": "7514068f45b73e3cabf9241c63a26436",
                    "__cs_import_ver": "34718392628248483",
                    "__input_archive_path": "//home/yabs-cs-sandbox/input-archive/518045646",
                    "__mysql_archive_resource_id": 1143985121,
                    "__bin_dbs_names": [
                        "st125",
                        "banner_update_05",
                        "st101",
                        "st089",
                        "st077",
                        "st053",
                        "st137",
                        "st065",
                        "st041",
                        "st017",
                        "st005",
                        "dssm_05",
                        "st029",
                        "st113",
                        "order",
                        "st149"
                    ]
                },
                {
                    "__bin_dbs_names": [
                        "st125",
                        "banner_update_05",
                        "resource_137",
                        "constant",
                        "st041",
                        "st065",
                        "dbe",
                        "domain",
                        "st005",
                        "banner_user_choice",
                        "phrase",
                        "resource_053",
                        "resource_089",
                        "st053",
                        "tsar_not_sharded",
                        "tsar_st_05",
                        "resource_077",
                        "resource_113",
                        "resource_041",
                        "formula",
                        "adaptive",
                        "dbis",
                        "url_cluster",
                        "resource_005",
                        "st137",
                        "st077",
                        "broadmatch",
                        "resource_065",
                        "resource_149",
                        "resource_101",
                        "st101",
                        "resource_017",
                        "resource_029",
                        "catalog",
                        "st017",
                        "organization",
                        "dssm_05",
                        "resource_125",
                        "dbds",
                        "goal",
                        "dsp_creative",
                        "st113",
                        "search_query",
                        "st089",
                        "auction_phrase",
                        "geo_segments",
                        "place",
                        "page_alg",
                        "st029",
                        "page_pos",
                        "order",
                        "st149"
                    ],
                    "__created_by_task": 519196023,
                    "__cs_import_out_digest": None,
                    "__cs_import_ver": [
                        "34718392628248483"
                    ],
                    "__import_completed": True,
                    "__input_archive_path": "//home/yabs-cs-sandbox/input-archive/518045646",
                    "__is_reusable": False,
                    "__mysql_archive_resource_id": 1143985121,
                    "__settings_spec": "",
                    "__settings_spec_md5": "7514068f45b73e3cabf9241c63a26436",
                    "__ttl_for_expiration_time": "90000.0",
                    "__reused_by_tasks": [
                        519362465,
                        520056483,
                        519985126,
                        520087624,
                        519460555,
                        519218860,
                        519337496,
                        520093507,
                        519242837,
                        519243288,
                        519274074,
                        519326299
                    ],
                },
                True
            ),
        ]
    )
    def test_skip_node_by_attributes(self, filter_attributes, node_attributes, expected):
        assert skip_node_by_attributes(filter_attributes, node_attributes) == expected
