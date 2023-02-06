insert into eats_billing_processor.deals(data, token, counterparty_type, counterparty_id,
                                         order_nr, timestamp, rule_name)
values ($$
{
    "version": "1",
    "kind": "place",
    "rule": "restaurant",
    "info": {
        "contract_id": "place_contract",
        "country_code": "RU",
        "id": "123456",
        "mvp": "place_mvp"
    }
}
$$, 'place_token', 'place', 'place_1', '123456', '2021-06-22T14:00:00+00:00', 'restaurant'),
($$
{
    "version": "1",
    "kind": "courier",
    "rule": "restaurant",
    "info": {
        "contract_id": "courier_contract",
        "country_code": "RU",
        "id": "123456",
        "mvp": "courier_mvp",
        "employment" : "courier_service"
    }
}
$$, 'courier_token', 'courier', 'courier_1', '123456', '2021-06-22T14:00:00+00:00', 'restaurant'),
($$
{
    "version": "1",
    "kind": "picker",
    "rule": "restaurant",
    "info": {
        "contract_id": "picker_contract",
        "country_code": "RU",
        "id": "123456",
        "mvp": "picker_mvp",
        "employment" : "self_employed"
    }
}
$$, 'picker_token', 'picker', 'picker_1', '123456', '2021-06-22T14:00:00+00:00', 'restaurant');
