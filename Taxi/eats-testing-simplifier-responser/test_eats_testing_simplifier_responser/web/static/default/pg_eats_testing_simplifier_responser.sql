insert into eats_testing_simplifier_responser.users_payments_methods(passport_uid, mock_usage, payment_methods)
values ('1', true,
        '[{"id": "VISA", "enable" : true},{"id": "MASTERCARD", "enable" : false},{"id": "googlepay", "enable" : true} ]'),
       ('2', true, '[{"id": "corp", "enable" : true}]'),
       ('3', false, '[{"id": "VISA1", "enable": false}]');
