/* consumers by tests */
INSERT INTO clients_schema.consumers (name) VALUES ('docker_integration_tests/user_has');

/* consumers old */
INSERT INTO clients_schema.consumers (name, service)
    VALUES
        ('launch', 'protocol'),
        ('client_protocol/launch', 'protocol'),
        ('driver_protocol/driver_polling_state', 'driver_protocol'),
        ('reposition_usages', 'reposition'),
        ('reposition_make_offer', 'reposition'),
        ('reposition_rule_violation', 'reposition'),
        ('nearestposition', 'protocol'),
        ('routestats', 'protocol'),
        ('zoneinfo', 'protocol'),
        ('taxiontheway', 'protocol'),
        ('softswitch_user_to_driver_call', 'softswitch'),
        ('softswitch_driver_to_user_call', 'softswitch'),
        ('communications', 'communications'),
        ('protocol/suggest', 'protocol'),
        ('taximeter', 'taximeter');

/* consumers new */
INSERT INTO clients_schema.consumers (name, service)
    VALUES
        ('reposition/usages', 'reposition'),
        ('reposition/make_offer', 'reposition'),
        ('reposition/rule_violation', 'reposition'),
        ('client_protocol/nearestposition', 'protocol'),
        ('client_protocol/routestats', 'protocol'),
        ('client_protocol/zoneinfo', 'protocol'),
        ('client_protocol/taxiontheway', 'protocol'),
        ('client_protocol/ordercommit', 'protocol'),
        ('client_protocol/createdraft', 'protocol'),
        ('protocol/taxiontheway', 'protocol'),
        ('softswitch_user/to_driver_call', 'softswitch'),
        ('softswitch/driver_to_user_call', 'softswitch'),
        ('communications/device_notify', 'communications'),
        ('taximeter/launch', 'taximeter'),
        ('taximeter/driver_polling_state', 'taximeter'),
        ('lookup/acquire', 'lookup'),
        ('cardstorage/payment_verifications', 'cardstorage'),
        ('grocery-api/modes', 'grocery-api'),
        ('grocery-cart/order-cycle', 'grocery-cart');
