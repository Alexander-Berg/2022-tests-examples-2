from taxi.antifraud.xaron.mover import lib

ROWS = [
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "10",
        "order_id": "11",
        "orders_to_deprive_subventions_from": [],
        "rules_additional_info": {},
        "rules_names_applied_today": None,
        "rules_names": [],
        "timestamp": 1,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "10",
        "order_id": "12",
        "orders_to_deprive_subventions_from": ["11"],
        "rules_additional_info": {},
        "rules_names_applied_today": [],
        "rules_names": ["ActiveRule1"],
        "timestamp": 2,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "10",
        "order_id": "13",
        "orders_to_deprive_subventions_from": ["11", "12"],
        "rules_additional_info": {},
        "rules_names_applied_today": ["ActiveRule1"],
        "rules_names": [],
        "timestamp": 3,
    },
    {
        "driver_clid": "400000537197",  # whitelisted
        "driver_license_personal_id": "pd",
        "driver_uuid": "10",
        "order_id": "14",
        "orders_to_deprive_subventions_from": ["11", "12", "13"],
        "rules_additional_info": {},
        "rules_names_applied_today": ["ActiveRule1"],
        "rules_names": [],
        "timestamp": 4,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "20",
        "order_id": "21",
        "orders_to_deprive_subventions_from": None,
        "rules_additional_info": {},
        "rules_names_applied_today": [],
        "rules_names": ["ActiveRule2", "ActiveRule3"],
        "timestamp": 21,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "20",
        "order_id": "22",
        "orders_to_deprive_subventions_from": [],
        "rules_additional_info": {},
        "rules_names_applied_today": [],
        "rules_names": ["ActiveRule3", "ActiveRule2"],
        "timestamp": 22,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "30",
        "order_id": "31",
        "orders_to_deprive_subventions_from": [],
        "rules_additional_info": {},
        "rules_names_applied_today": ["ActiveRule4"],
        "rules_names": ["ActiveRule4"],
        "timestamp": 31,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "30",
        "order_id": "32",
        "orders_to_deprive_subventions_from": ["31"],
        "rules_additional_info": {},
        "rules_names_applied_today": [],
        "rules_names": None,
        "timestamp": 32,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "40",
        "order_id": "41",
        "orders_to_deprive_subventions_from": [],
        "rules_additional_info": None,
        "rules_names_applied_today": ["ActiveRule4"],
        "rules_names": [],
        "timestamp": 41,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "40",
        "order_id": "42",
        "orders_to_deprive_subventions_from": ["41"],
        "rules_additional_info": {},
        "rules_names_applied_today": [],
        "rules_names": [],
        "timestamp": 42,
    },
    {
        "driver_clid": "some_clid",
        "driver_license_personal_id": "pd",
        "driver_uuid": "50",
        "order_id": "51",
        "orders_to_deprive_subventions_from": None,
        "rules_additional_info": None,
        "rules_names_applied_today": None,
        "rules_names": None,
        "timestamp": 51,
    },
]


def get_deprived_orders_from_rows(rows, deprive_config):
    depriver = lib.Depriver(deprive_config)
    for row in rows:
        depriver.consume(row)
    return depriver.orders()


def test_deprive_only():
    config = [{"rule_name": "ActiveRule1", "description": "", "deprive_from_future": False, "deprive_from_past": False}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([item["order_id"] for item in orders]) == ["12"]


def test_deprive_from_future_only():
    config = [{"rule_name": "ActiveRule1", "description": "", "deprive": False, "deprive_from_past": False}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([item["order_id"] for item in orders]) == ["11"]


def test_deprive_from_past_only():
    config = [{"rule_name": "ActiveRule1", "description": "", "deprive": False, "deprive_from_future": False}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([item["order_id"] for item in orders]) == ["13"]


def test_deprive_all():
    config = [{"rule_name": "ActiveRule1", "description": ""}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([item["order_id"] for item in orders]) == ["11", "12", "13"]


def test_deprive_order():
    # проверяем, что из всех правил выбирается первое по порядку
    config = [{"rule_name": "ActiveRule2", "description": ""}, {"rule_name": "ActiveRule3", "description": ""}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([item["order_id"] for item in orders]) == ["21", "22"]
    assert [item["reason"] for item in orders] == ["ActiveRule2", "ActiveRule2"]

    config = [{"rule_name": "ActiveRule3", "description": ""}, {"rule_name": "ActiveRule2", "description": ""}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([item["order_id"] for item in orders]) == ["21", "22"]
    assert [item["reason"] for item in orders] == ["ActiveRule3", "ActiveRule3"]


def test_deprive_priority():
    # проверяем, что если один и тот же заказ забанен просто так, из прошлого и из будущего, мы получим логе правильную запись
    config = [{"rule_name": "ActiveRule4", "description": ""}]
    orders = get_deprived_orders_from_rows(ROWS, config)
    assert sorted([(item["order_id"], item["info"]["type"]) for item in orders]) == [("31", "deprive"), ("41", "deprive_from_past")]


def test_ts2date():
    assert lib.ts2date(1626210000) == "2021-07-14"
    assert lib.ts2date(1626210000 - 1) == "2021-07-13"
