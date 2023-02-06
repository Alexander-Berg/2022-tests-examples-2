# DROP SCHEMA IF EXISTS eats_testing_simplifier_responser CASCADE;
CREATE SCHEMA IF NOT EXISTS eats_testing_simplifier_responser;

CREATE TABLE IF NOT EXISTS eats_testing_simplifier_responser.users_payments_methods(
  passport_uid   VARCHAR(100)    PRIMARY KEY,
  mock_usage BOOLEAN         NOT NULL,
  payment_methods      TEXT    NOT NULL
);
