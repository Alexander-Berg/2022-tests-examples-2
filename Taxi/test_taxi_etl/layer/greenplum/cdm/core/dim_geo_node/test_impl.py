from dmp_suite.test_utils import DmpTestCase
from taxi_etl.layer.greenplum.cdm.geo.dim_geo_node_w_duplicates.impl import (
    build_hierarchy_linking,
    traverse_down,
    flatten_tariff_zones,
    hierarchy_from_agglomerations
)
from .data.example_hierarchy import (
    EXAMPLE_HIERARCHY, 
    CURRENCY_DICT, 
    COUNTRY_CODE_DICT,
    COUNTRY_NAME_EN_DICT,
    AGGLOMERATION_NAME_DICT
)
from .data.expected import EXPECTED_ITEMS, EXPECTED_OP, EXPECTED_PLUS_FI

for item in EXAMPLE_HIERARCHY:
    item.update({
        'currency_code': CURRENCY_DICT[item.get('country_short_code')],
        'country_short_code': COUNTRY_CODE_DICT[item.get('country_short_code')][0],
        'country_code': COUNTRY_CODE_DICT[item.get('country_short_code')][1],
    })
for item in EXPECTED_ITEMS:
    item.update({
        'currency_code': CURRENCY_DICT[item.get('country_code_impl')],
        'country_short_code': COUNTRY_CODE_DICT[item.get('country_code_impl')][0],
        'country_code': COUNTRY_CODE_DICT[item.get('country_code_impl')][1],
        'country_name_en': COUNTRY_NAME_EN_DICT[item.get('country_name_ru')],
        'agglomeration_name_en': AGGLOMERATION_NAME_DICT[item.get('agglomeration_node_id')][0],
        'agglomeration_name_ru': AGGLOMERATION_NAME_DICT[item.get('agglomeration_node_id')][1],
        'short_population_group_code': item.get('population_group')[3:] if item.get('population_group') else None,
    })


class TestHierarchy(DmpTestCase):
    def test_hierarchy_linking(self):
        nodes = [
            {
                'node_id': 'br_root',
                'child_geo_nodes': ['br_foo', 'br_buz'],
            },
            {
                'node_id': 'br_foo',
                'child_geo_nodes': ['br_bar'],
                'parent_priority': 1,
            },
            {
                'node_id': 'br_bar',
                'child_geo_nodes': []
            },
            {
                'node_id': 'br_buz',
                'child_geo_nodes': ['br_bar', 'br_gul'],
                'parent_priority': 0,
            },
            {
                'node_id': 'br_gul',
                'child_geo_nodes': [],
                'parent_priority': None,
            }
        ]

        expected_items = {
            'br_root': {
                'node_id': 'br_root',
                'child_geo_nodes': ['br_foo', 'br_buz'],
                'parent_priority': 0,
                'reachable': True,
            },
            'br_foo': {
                'node_id': 'br_foo',
                'child_geo_nodes': ['br_bar'],
                'parent_priority': 1,
                'reachable': True,
            },
            'br_bar': {
                'node_id': 'br_bar',
                'child_geo_nodes': [],
                'parent_priority': 0,
                'reachable': True,
            },
            'br_buz': {
                'node_id': 'br_buz',
                'child_geo_nodes': ['br_bar', 'br_gul'],
                'parent_priority': 0,
                'reachable': True,
            },
            'br_gul': {
                'node_id': 'br_gul',
                'child_geo_nodes': [],
                'parent_priority': 0,
                'reachable': True,
            }
        }

        expected_c2p = {
            'br_buz': [('br_root', 0)],
            'br_foo': [('br_root', 0)],
            'br_bar': [('br_foo', 1), ('br_buz', 0)],
            'br_gul': [('br_buz', 0)]
        }

        items, child_to_parents = build_hierarchy_linking(nodes, 'br_root')

        self.assertEqual(items, expected_items)
        self.assertEqual(child_to_parents, expected_c2p)

    def test_traverse_down(self):
        expected_items = filter(lambda x: x.get('root_node_id') == 'op_root', EXPECTED_ITEMS)

        items_dict, c2p = build_hierarchy_linking(EXAMPLE_HIERARCHY, 'op_root')
        items = traverse_down('op', items_dict, c2p, ['en'])
        self.assertItemsEqual(items, expected_items)

    def test_hierarchy_from_agglomerations(self):
        expected_hier = filter(lambda x: x.get('root_node_id') == 'op_root', EXPECTED_ITEMS)

        hier_op = hierarchy_from_agglomerations('op', EXAMPLE_HIERARCHY, ['en'])
        self.assertItemsEqual(hier_op, expected_hier)

    def test_flatten_tariff_zones(self):

        items_op_dict, c2p_op = build_hierarchy_linking(EXAMPLE_HIERARCHY, 'op_root')
        items_op = traverse_down('op', items_op_dict, c2p_op, ['en'])
        flatten_op = flatten_tariff_zones(items_op)

        self.assertItemsEqual(flatten_op, EXPECTED_OP)

        items_fi_dict, c2p_fi = build_hierarchy_linking(EXAMPLE_HIERARCHY, 'fi_root')
        items_fi = traverse_down('fi', items_fi_dict, c2p_fi, ['en'])
        flatten_op_fi = flatten_tariff_zones(list(items_op) + list(items_fi))

        self.assertItemsEqual(flatten_op_fi, EXPECTED_OP + EXPECTED_PLUS_FI)
