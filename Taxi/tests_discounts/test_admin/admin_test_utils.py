import copy
import json

DEFAULT_QUERIES = [
    """
    INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
    VALUES ('testsuite_zone',true,'tariff_zone') """,
    """
    INSERT INTO discounts.discounts_entities(
        description,
        discount_class,
        enabled,
        select_params,
        calculation_params,
        discount_method
    )
    VALUES ('testsuite_discount', 'valid_class',false,
    \'{"classes": ["econom"],
    "datetime_params": {
        "date_from": "2019-01-01T00:00:00",
        "timezone_type": "utc"
    },        "geoarea_a" : "Himki",
        "geoarea_b" : "Aprelevka",
    "discount_target": "all"}\',
    \'{"round_digits": 3,
    "calculation_method": "calculation_table",
    "discount_calculator": {"table": [{"cost": 100.0, "discount": 0.2}]}}\',
    'full')""",
    """INSERT INTO
     discounts.user_discounts(discount_series_id,reference_entity_id)
    VALUES ('0120e1',1)""",
    """INSERT INTO discounts.discounts_lists(
    zonal_list_id,reference_entity_id,prev_item,next_item)
    VALUES (1,1,NULL,NULL)""",
]

DISCOUNT_LIST_QUERIES = [
    """
    INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
    VALUES ('testsuite_zone',true,'tariff_zone') """,
    """
    INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
    VALUES ('testsuite_zone_2',true,'tariff_zone') """,
    """
    INSERT INTO discounts.discounts_entities(
        description,
        discount_class,
        enabled,
        select_params,
        calculation_params,
        discount_method
    )
    VALUES ('testsuite_discount1', 'valid_class', false,
    \'{"classes": ["econom"],
    "datetime_params": {
        "date_from": "2019-01-01T00:00:00",
        "timezone_type": "utc"
    },
    "discount_target": "all"}\',
    \'{"round_digits": 3,
    "calculation_method": "calculation_table",
    "discount_calculator": {"table": [{"cost": 100.0, "discount": 0.2}]}}\',
    'full'),
    ('testsuite_discount2', 'valid_class', false,
    \'{"classes": ["econom"],
    "datetime_params": {
        "date_from": "2019-01-01T00:00:00",
        "timezone_type": "utc"
    },
    "discount_target": "all"}\',
    \'{"round_digits": 3,
    "calculation_method": "calculation_table",
    "discount_calculator": {"table": [{"cost": 100.0, "discount": 0.2}]}}\',
    'full')""",
    """INSERT INTO
     discounts.user_discounts(discount_series_id,reference_entity_id)
    VALUES ('0120e1',1), ('deafbeef',2)""",
    """INSERT INTO discounts.discounts_lists(
    zonal_list_id,reference_entity_id,prev_item,next_item)
    VALUES (1,1,NULL,2), (1,2,1,NULL), (2,1,NULL,4), (2,2,3,NULL)""",
]


DEFAULT_DB_STATE = {
    'zonal_lists': [
        {
            'zonal_list_id': 1,
            'zone_name': 'testsuite_zone',
            'enabled': True,
            'zone_type': 'tariff_zone',
        },
    ],
    'discounts_entities': [
        {
            'reference_entity_id': 1,
            'draft_id': None,
            'discount_class': 'valid_class',
            'prev_entity': None,
            'description': 'testsuite_discount',
            'enabled': False,
            'select_params': {
                'classes': ['econom'],
                'datetime_params': {
                    'date_from': '2019-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
                'discount_target': 'all',
                'geoarea_a': 'Himki',
                'geoarea_b': 'Aprelevka',
            },
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'discount_method': 'full',
            'driver_less_coeff': None,
            'update_meta_info': None,
            'discount_meta_info': {},
        },
    ],
    'discounts_lists': [
        {
            'id': 1,
            'zonal_list_id': 1,
            'reference_entity_id': 1,
            'prev_item': None,
            'next_item': None,
        },
    ],
    'user_discounts': [
        {'id': 1, 'discount_series_id': '0120e1', 'reference_entity_id': 1},
    ],
}

# Generated via `tvmknife unittest service -s 123 -d 123321`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIexC5wwc:Q9I_85'
    'oQtOPXLu9Ds2xuQNWKPxksLjXJ4AqHbvuCulWBk5N'
    'O2CXoV4FoNn-5uN4gjYLAgq19i3AV5_hfSdGYfTph'
    'Ibm6wzagYf8nMoSTWW_7aBoY2VPHmmhJF9zDcN2Au'
    'MnuEXa5CTym5hyAM3g8lq-BfvL16ZAg7iTGOxipklY'
)
DRAFT_ID = '1000'

DEFAULT_DISCOUNTS_HEADERS = {
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-YaTaxi-Draft-Author': 'user',
    'X-YaTaxi-Draft-Approvals': 'user3,user4',
    'X-YaTaxi-Draft-Tickets': 'ticket-1',
    'X-YaTaxi-Draft-Id': DRAFT_ID,
}


def patch_db_state(state, append_patch=None, update_patch=None):
    new_state = copy.deepcopy(state)
    if update_patch:
        for item in update_patch:
            if item in state:
                new_state[item] = update_patch[item]
    if append_patch:
        for item in append_patch:
            if item in state:
                new_state[item] += append_patch[item]
    return new_state


def patch_db(pgsql, queries):
    cursor = pgsql['discounts'].conn.cursor()
    for query in queries:
        cursor.execute(query)
    cursor.close()


def assert_sorted(lhs, rhs, sort_key):
    assert sorted(lhs, key=lambda x: x[sort_key]) == sorted(
        rhs, key=lambda x: x[sort_key],
    )


def assert_sorted_ignore_date(lhs, rhs, sort_key):
    lhs = sorted(lhs, key=lambda x: x[sort_key])
    rhs = sorted(rhs, key=lambda x: x[sort_key])
    for (l_item, r_item) in zip(lhs, rhs):
        assert l_item.keys() == r_item.keys()
        for key in l_item.keys():
            if key == 'update_meta_info':
                if l_item[key] is None:
                    continue
                assert l_item[key].keys() == r_item[key].keys()
                for sub_key in l_item[key].keys():
                    if sub_key == 'date':
                        continue
                    assert l_item[key][sub_key] == r_item[key][sub_key]
            else:
                assert l_item[key] == r_item[key]


class DBState:
    def __init__(self, pgsql):
        self.pgsql = pgsql
        self.query_template = 'SELECT * FROM discounts.{}'

    def _select_from(self, table):
        cursor = self.pgsql['discounts'].conn.cursor()
        cursor.execute(self.query_template.format(table))
        res = []
        for row in cursor.fetchall():
            res.append({})
            for col in range(len(cursor.description)):
                res[len(res) - 1][cursor.description[col][0]] = row[col]
        return res

    @property
    def user_discounts(self):
        return self._select_from('user_discounts')

    @property
    def discounts_entities(self):
        return self._select_from('discounts_entities')

    @property
    def zonal_lists(self):
        return self._select_from('zonal_lists')

    @property
    def discounts_lists(self):
        return self._select_from('discounts_lists')


async def create_discount(
        request, taxi_discounts, pgsql, expected_code, headers,
):
    db_state = DBState(pgsql)
    expected_discount = copy.deepcopy(request['discount'])
    expected_discount['reference_entity_id'] = (
        len(db_state.discounts_entities) + 1
    )

    if headers:
        expected_discount['update_meta_info'] = {
            'user_login': headers['X-YaTaxi-Draft-Author'],
            'tickets': [headers['X-YaTaxi-Draft-Tickets']],
        }
    response = await taxi_discounts.post(
        'v1/admin/discounts', data=json.dumps(request), headers=headers,
    )
    response_2 = await taxi_discounts.post(
        'v1/admin/discounts', data=json.dumps(request), headers=headers,
    )
    assert response.json() == response_2.json()

    assert response.status_code == expected_code, (
        response.status_code,
        response.json(),
    )
    if expected_code == 200:
        response_json = response.json()
        assert 'discount' in response_json
        created_discount = response_json['discount']
        if (
                'update_meta_info' in created_discount
                and 'date' in created_discount['update_meta_info']
        ):
            del created_discount['update_meta_info']['date']
        if 'limit_id' in created_discount:
            del created_discount['limit_id']

        assert created_discount == expected_discount
