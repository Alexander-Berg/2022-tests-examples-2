import asyncio

import pytest
import pytz

DEFAULT_HEADERS = {
    'X-YaTaxi-Draft-Id': 'test_draft_id',
    'X-YaTaxi-Multidraft-Id': 'test_multi_draft_id',
}

PARAMETRIZE_OK: list = [
    pytest.param(
        None,
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'tanker_key': 'geo_nodes.br_moscow_adm',
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
            'macro_managers': ['mikhailra'],
            'meta_tags': ['agglomeration_with_only_br_parent'],
        },
        id='ok_agglomeration',
    ),
    pytest.param(
        None,
        {
            'parents': ['br_root'],
            'children': ['br_moskovskaja_obl'],
            'hierarchy_type': 'BR',
            'name': 'br_tsentralnyj_fo',
            'tanker_key': 'name.br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
        },
        {
            'children': ['br_moskovskaja_obl'],
            'hierarchy_type': 'BR',
            'name': 'br_tsentralnyj_fo',
            'tanker_key': 'name.br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parents': ['br_russia'],
            'region_id': '3',
            'tags': ['federal district'],
        },
        id='change_parent',
    ),
    pytest.param(
        None,
        {
            'hierarchy_type': 'BR',
            'name': 'br_moscow_adm',
            'tanker_key': 'name.br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'oebs_mvp_id': 'updated',
            'parents': ['br_moscow'],
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'region_id': '11111',
        },
        {
            'hierarchy_type': 'BR',
            'name': 'br_moscow_adm',
            'tanker_key': 'name.br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moscow'],
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'region_id': '213',
        },
        id='update_oebs_mvp_id',
    ),
    pytest.param(
        None,
        {
            'hierarchy_type': 'BR',
            'name': 'br_root',
            'tanker_key': 'name.br_root',
            'name_en': 'Root',
            'name_ru': 'Root',
            'node_type': 'root',
            'children': ['br_russia', 'br_kazakhstan'],
            'tags': ['test_tag'],
        },
        {
            'children': ['br_russia', 'br_kazakhstan'],
            'hierarchy_type': 'BR',
            'name': 'br_root',
            'tanker_key': 'name.br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        id='ok_root',
    ),
    pytest.param(
        None,
        {
            'parents': ['br_root'],
            'children': ['br_tsentralnyj_fo'],
            'hierarchy_type': 'BR',
            'name': 'br_russia',
            'tanker_key': 'name.br_russia',
            'currency': 'RUB',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
        },
        {
            'children': ['br_tsentralnyj_fo'],
            'hierarchy_type': 'BR',
            'currency': 'RUB',
            'name': 'br_russia',
            'tanker_key': 'name.br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'region_id': '225',
            'node_type': 'country',
            'operational_managers': ['berenda'],
            'parents': ['br_root'],
        },
        id='ok_country',
    ),
    pytest.param(
        None,
        {
            'name': 'br_new',
            'tanker_key': 'name.br_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'node',
            'hierarchy_type': 'BR',
            'parents': ['br_moscow', 'fi_root', 'op_root'],
            'oebs_mvp_id': 'new_oebs_mvp_id',
            'region_id': '123',
            'population': 22324,
            'tariff_zones': ['tomsk', 'novosib'],
            'tags': ['tag'],
            'regional_managers': ['test'],
            'operational_managers': ['test'],
            'macro_managers': ['test'],
        },
        None,
        id='new_br',
    ),
    pytest.param(
        None,
        {
            'name': 'br_new',
            'tanker_key': 'name.br_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'node',
            'hierarchy_type': 'BR',
            'parents': ['br_moscow', 'fi_root', 'op_root'],
            'oebs_mvp_id': 'new_oebs_mvp_id',
            'region_id': '123',
            'population': 22324,
            'tariff_zones': ['almaty'],
            'tags': ['tag'],
            'regional_managers': ['test'],
            'operational_managers': ['test'],
            'macro_managers': ['test'],
            'meta_tags': ['invalid_currency'],
        },
        None,
        id='new_with_invalid_currency_and_meta_tags_invalid_currency',
    ),
    pytest.param(
        None,
        {
            'name': 'br_new',
            'tanker_key': 'name.br_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'agglomeration',
            'hierarchy_type': 'BR',
            'parents': ['br_moskovskaja_obl'],
            'oebs_mvp_id': 'new_oebs_mvp_id',
            'region_id': '123',
            'population': 22324,
            'tariff_zones': ['tomsk'],
            'tags': ['tag'],
            'regional_managers': ['test'],
            'operational_managers': ['test'],
            'macro_managers': ['test'],
            'meta_tags': ['agglomeration_with_only_br_parent'],
        },
        None,
        id='agglomeration_without_all_parents_and_with_meta_tags',
    ),
    pytest.param(
        None,
        {
            'name': 'fi_new',
            'tanker_key': 'name.fi_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'node',
            'hierarchy_type': 'FI',
            'parents': ['fi_root'],
            'region_id': '123',
        },
        None,
        id='new_fi_with_all_fields',
    ),
    pytest.param(
        {
            'name': 'op_new',
            'tanker_key': 'name.op_new',
            'name_en': '  New\t  \tOp  ',
            'name_ru': '  Новый\t\tОП  ',
            'node_type': 'node',
            'hierarchy_type': 'OP',
            'parents': ['op_root'],
            'region_id': '123',
            'sort_priority': 1,
            'parent_priority': 1,
        },
        {
            'name': 'op_new',
            'tanker_key': 'name.op_new',
            'name_en': 'New Op',
            'name_ru': 'Новый ОП',
            'node_type': 'node',
            'hierarchy_type': 'OP',
            'parents': ['op_root'],
            'region_id': '123',
            'sort_priority': 1,
            'parent_priority': 1,
        },
        None,
        id='new_op_with_all_fields',
    ),
]


PARAMETRIZE_WITH_ERROR: list = [
    pytest.param(
        {
            'name': 'br_new',
            'tanker_key': 'name.br_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'agglomeration',
            'hierarchy_type': 'BR',
            'parents': ['br_moskovskaja_obl', 'fi_root'],
            'oebs_mvp_id': 'new_oebs_mvp_id',
            'region_id': '123',
            'population': 22324,
            'tariff_zones': ['tomsk'],
            'tags': ['tag'],
            'regional_managers': ['test'],
            'operational_managers': ['test'],
            'macro_managers': ['test'],
            'meta_tags': ['agglomeration_with_only_br_parent'],
        },
        {
            'code': 'AGGLOMERATION_MUST_HAVE_PARENTS_FROM_HIERARCHIES',
            'message': 'Need hierarchies: BR. Got: BR,FI',
        },
        id='with_meta_tags_agglomeration_with_only_br_parent_and_two_parents',
    ),
    pytest.param(
        {
            'children': ['br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
            'macro_managers': ['mikhailra'],
            'meta_tags': ['agglomeration_with_only_br_parent'],
        },
        {
            'code': 'CHANGING_CHILDREN_FORBIDDEN',
            'message': (
                'Changing children is forbidden. '
                'Old children: br_moscow_adm, br_moscow_middle_region. '
                'New children: br_moscow_middle_region'
            ),
        },
        id='with_meta_tags_agglomeration_with_only_br_parent_and_two_parents',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'OEBS_MVP_ID_REQUIRED',
            'message': (
                'GeoNode with type agglomeration '
                'or with agglomeration in parents '
                'must have oebs_mvp_id'
            ),
        },
        id='agglomeration_without_oebs_mvp_id',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'OEBS_MVP_ID_REQUIRED',
            'message': (
                'GeoNode with type agglomeration '
                'or with agglomeration in parents '
                'must have oebs_mvp_id'
            ),
        },
        id='agglomeration_without_oebs_mvp_id',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'fi_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'AGGLOMERATION_MUST_HAVE_PARENTS_FROM_HIERARCHIES',
            'message': 'Need hierarchies: BR,FI,OP. Got: BR,FI',
        },
        id='agglomeration_without_all_parents',
    ),
    pytest.param(
        {
            'name': 'br_new',
            'tanker_key': 'name.br_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'node',
            'hierarchy_type': 'BR',
            'parents': ['br_moscow', 'fi_root', 'op_root'],
            'oebs_mvp_id': 'new_oebs_mvp_id',
            'region_id': '123',
            'population': 22324,
            'tariff_zones': ['almaty'],
            'tags': ['tag'],
            'regional_managers': ['test'],
            'operational_managers': ['test'],
            'macro_managers': ['test'],
        },
        {
            'code': 'INVALID_CURRENCY',
            'message': 'Tariff zones must have the same currency with country',
        },
        id='with_invalid_currency',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'tariff_zones': ['moscow'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_root', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'INVALID_TARIFF_ZONES',
            'message': 'Tariff zones must be under country.',
        },
        id='tariff_zone_not_under_country',
    ),
    pytest.param(
        {
            'children': ['br_moskovskaja_obl'],
            'hierarchy_type': 'BR',
            'name': 'br_tsentralnyj_fo',
            'tanker_key': 'name.br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parents': ['br_russia'],
            'region_id': '3',
            'tags': ['federal district'],
            'tariff_zones': ['tomsk'],
        },
        {
            'code': 'TARIFF_ZONE_NOT_UNDER_AGGLOMERATION',
            'message': 'Tariff zone must be under agglomeration',
        },
        id='tariff_zone_not_under_agglomeration',
    ),
    pytest.param(
        {
            'parents': ['br_root'],
            'children': ['br_tsentralnyj_fo'],
            'hierarchy_type': 'BR',
            'name': 'br_russia',
            'tanker_key': 'name.br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
        },
        {
            'code': 'INVALID_CURRENCY',
            'message': (
                'For GeoNode with node_type=country currency is required.'
            ),
        },
        id='country_without_currency',
    ),
    pytest.param(
        {
            'hierarchy_type': 'BR',
            'name': 'br_root',
            'tanker_key': 'name.br_root',
            'name_en': 'Root',
            'currency': 'RUB',
            'name_ru': 'Root',
            'node_type': 'root',
            'children': ['br_russia', 'br_kazakhstan'],
        },
        {
            'code': 'INVALID_CURRENCY',
            'message': (
                'Only for GeoNode with node_type=country currency is allowed.'
            ),
        },
        id='root_with_currency',
    ),
    pytest.param(
        {
            'children': ['br_tsentralnyj_fo'],
            'hierarchy_type': 'BR',
            'currency': 'RUB',
            'name': 'br_russia',
            'tanker_key': 'name.br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
            'operational_managers': ['berenda'],
            'parents': ['br_moscow_adm'],
        },
        {
            'code': 'CYCLE_REFERENCING',
            'message': 'Cyclic reference detected: cannot set child as parent',
        },
        id='reference_from_russia_to_br_moscow_adm',
    ),
    pytest.param(
        {
            'parents': ['br_root'],
            'children': ['br_invalid'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'node',
            'oebs_mvp_id': 'MSKc',
        },
        {
            'code': 'GEO_NODE_NOT_FOUND',
            'message': 'Not found geo_nodes: {\'br_invalid\'}',
        },
        id='not_found_children',
    ),
    pytest.param(
        {
            'parents': ['br_invalid'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'node',
            'oebs_mvp_id': 'MSKc',
        },
        {
            'code': 'GEO_NODE_NOT_FOUND',
            'message': 'Not found geo_nodes: {\'br_invalid\'}',
        },
        id='not_found_parents',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'tariff_zones': ['invalid'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'TARIFF_ZONES_NOT_FOUND',
            'message': 'Tariff zones not found: [\'invalid\']',
        },
        id='invalid_tariff_zone',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'operational_managers': ['susloparov'],
            'parents': ['br_moscow', 'fi_root', 'op_root'],
        },
        {
            'code': 'CYCLE_REFERENCING',
            'message': 'Cyclic reference detected: cannot set child as parent',
        },
        id='self_in_parents',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'operational_managers': ['susloparov'],
            'parents': ['br_moskovskaja_obl', 'fi_root', 'fi_emea', 'op_root'],
        },
        {
            'code': 'INCORRECT_PARENT',
            'message': 'In FI hierarchy only one parent is allowed',
        },
        id='two_fi_parents',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'INCORRECT_PARENT',
            'message': 'BR node must have at least one BR parent',
        },
        id='without_br_parent',
    ),
    pytest.param(
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'br_root', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
        },
        {
            'code': 'INCORRECT_PARENT',
            'message': 'In BR hierarchy only one parent is allowed',
        },
        id='two_br_parents',
    ),
    pytest.param(
        {
            'hierarchy_type': 'FI',
            'name': 'fi_moscow',
            'tanker_key': 'name.fi_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Moscow',
            'node_type': 'node',
        },
        {
            'code': 'INCORRECT_PARENT',
            'message': 'FI node must have at least one FI parent',
        },
        id='fi_without_parent',
    ),
    pytest.param(
        {
            'hierarchy_type': 'BR',
            'parents': ['br_moscow'],
            'name': 'br_root',
            'tanker_key': 'name.br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'code': 'ROOT_CAN_NOT_HAVE_PARENTS',
            'message': 'Root can not have parents.',
        },
        id='bad_root_name',
    ),
    pytest.param(
        {
            'hierarchy_type': 'BR',
            'name': 'br_invalid',
            'tanker_key': 'name.br_invalid',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'code': 'INVALID_GEO_NODE_ROOT_NAME',
            'message': 'GeoNode root must be \'br_root\' not \'br_invalid\'',
        },
        id='bad_root_name',
    ),
    pytest.param(
        {
            'hierarchy_type': 'OP',
            'name': 'op_agglomeration_not_br',
            'tanker_key': 'name.op_agglomeration_not_br',
            'name_en': 'Agglomeration not in br',
            'name_ru': 'Агломерация не в базовая иерархия',
            'node_type': 'agglomeration',
        },
        {
            'code': 'AGGLOMERATION_NOT_IN_BR',
            'message': (
                'Node(op_agglomeration_not_br) which '
                'has agglomeration in parents '
                'or type agglomeration must have hierarchy_type BR'
            ),
        },
        id='agglomeration_not_br',
    ),
    pytest.param(
        {
            'hierarchy_type': 'BR',
            'name': 'invalid',
            'tanker_key': 'name.invalid',
            'name_en': 'Invalid name',
            'name_ru': 'Не правильное имя',
            'node_type': 'node',
        },
        {
            'code': 'INVALID_GEO_NODE_NAME',
            'message': (
                'GeoNode name must match \'^br_([A-Za-z0-9,_\\-+])+$\'.'
            ),
        },
        id='invalid_name',
    ),
    pytest.param(
        {
            'name': 'op_ new',
            'tanker_key': 'name.op_new',
            'name_en': '  New',
            'name_ru': '  Новый',
            'node_type': 'node',
            'hierarchy_type': 'OP',
            'parents': ['op_root'],
            'region_id': '123',
            'sort_priority': 1,
            'parent_priority': 1,
        },
        {
            'code': 'INVALID_GEO_NODE_NAME',
            'message': (
                'GeoNode name must match \'^op_([A-Za-z0-9,_\\-+])+$\'.'
            ),
        },
        id='invalid_op_name',
    ),
    pytest.param(
        {
            'hierarchy_type': 'FI',
            'name': 'fi_root',
            'tanker_key': 'name.fi_root',
            'name_en': 'Tariff zone not in br',
            'name_ru': 'Tariff zone not in br',
            'node_type': 'root',
            'tariff_zones': ['moscow'],
        },
        {
            'code': 'TARIFF_ZONE_NOT_IN_BR_HIERARCHY',
            'message': (
                'Node(fi_root) with not BR hierarchy can not have tariff zones'
            ),
        },
        id='tariff_zone_not_in_br',
    ),
    pytest.param(
        {
            'name': 'br_new',
            'tanker_key': 'name.br_new',
            'name_en': 'New',
            'name_ru': 'New',
            'node_type': 'node',
            'hierarchy_type': 'BR',
            'parents': ['br_moscow', 'fi_root', 'op_root'],
            'oebs_mvp_id': 'new_oebs_mvp_id',
            'region_id': '123',
            'population': 22324,
            'tariff_zones': ['moscow'],
            'tags': ['tag'],
            'regional_managers': ['test'],
            'operational_managers': ['test'],
            'macro_managers': ['test'],
        },
        {
            'code': 'TARIFF_ZONE_ALREADY_IN_GEO_NODE',
            'message': 'Tariff zone already in GeoNode',
        },
        id='tariff_zone_already_in_geo_node',
    ),
]


@pytest.mark.parametrize('body, expected_content', PARAMETRIZE_WITH_ERROR)
@pytest.mark.parametrize(
    'url', ['v1/admin/geo-node/', 'v1/admin/geo-node/check/'],
)
@pytest.mark.filldb()
async def test_v1_admin_geo_node_put_with_error(
        web_app_client, body, expected_content, url,
):
    str_handler = 'post' if 'check' in url else 'put'
    handler = getattr(web_app_client, str_handler)

    response = await handler(url, json=body, headers=DEFAULT_HEADERS)
    assert response.status == 400
    assert await response.json() == expected_content


@pytest.mark.parametrize('check_body, body, current', PARAMETRIZE_OK)
@pytest.mark.filldb()
async def test_v1_admin_geo_node_put_ok(
        web_app_client, check_body, body, current, mocked_time,
):
    if check_body is None:
        check_body = body
    name = body['name']

    for tariff_zone in body.get('tariff_zones', []):
        expected_content = (
            {'oebs_mvp_id': current['oebs_mvp_id']}
            if current
            else {'oebs_mvp_id': ''}
        )
        response = await web_app_client.get(
            'v1/geo_nodes/get_mvp_oebs_id',
            params={'tariff_zone': tariff_zone},
        )
        assert response.status == 200, await response.json()
        assert await response.json() == expected_content

    response = await web_app_client.get(
        'v1/admin/geo-node/', params={'name': name},
    )

    if current:
        assert await response.json() == current
    else:
        assert await response.json() == {
            'code': 'NOT_FOUND',
            'message': f'GeoNode with name="{name}" not found',
        }
    response = await web_app_client.post(
        'v1/admin/geo-node/check/', json=check_body,
    )
    assert response.status == 200, await response.json()
    expected_check = {
        'change_doc_id': name,
        'data': body,
        'diff': {'new': body},
    }
    if current:
        expected_check['diff']['current'] = current

    assert await response.json() == expected_check

    response = await web_app_client.put(
        'v1/admin/geo-node/', json=body, headers=DEFAULT_HEADERS,
    )
    assert response.status == 200, await response.json()
    response = await web_app_client.get(
        'v1/admin/geo-node/', params={'name': body['name']},
    )
    assert response.status == 200
    assert await response.json() == body

    await web_app_client.app['context'].oebs_mvp_cache.refresh_cache()

    mocked_time.sleep(1)

    for tariff_zone in body.get('tariff_zones', []):
        response = await web_app_client.get(
            'v1/geo_nodes/get_mvp_oebs_id',
            params={'tariff_zone': tariff_zone},
        )
        assert response.status == 200
        assert await response.json() == {'oebs_mvp_id': body['oebs_mvp_id']}
        now = mocked_time.now().replace(tzinfo=pytz.utc).isoformat()
        response = await web_app_client.get(
            'v1/geo_nodes/get_mvp_oebs_id',
            params={'tariff_zone': tariff_zone, 'dt': now},
        )
        assert response.status == 200
        assert await response.json() == {'oebs_mvp_id': body['oebs_mvp_id']}


async def test_v1_admin_geo_node_put_ok_several_times(web_app_client):
    body = {
        'parents': ['br_root'],
        'children': ['br_moskovskaja_obl'],
        'hierarchy_type': 'BR',
        'name': 'br_tsentralnyj_fo',
        'tanker_key': 'name.br_tsentralnyj_fo',
        'name_en': 'Central Federal District',
        'name_ru': 'Центральный ФО',
        'node_type': 'node',
    }
    tasks = [
        web_app_client.put(
            'v1/admin/geo-node/', json=body, headers=DEFAULT_HEADERS,
        )
        for _ in range(3)
    ]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        assert response.status == 200, await response.content.read()
        assert await response.content.read() == b''
