DROP SCHEMA IF EXISTS ridehistory CASCADE;

CREATE SCHEMA ridehistory;

-- VERSION 1

-- ridehistory orders cache to search order_ids by user;
-- is_hidden is needed not to load hidden orders from yt and clean
-- hidden_orders table without checking that order is cleaned from user_index
CREATE TABLE ridehistory.user_index
(
  order_id            VARCHAR       NOT NULL,
  phone_id            VARCHAR       NOT NULL,
  user_uid            VARCHAR       NOT NULL,
  order_created_at    TIMESTAMPTZ   NOT NULL,
  seen_unarchived_at  TIMESTAMPTZ   NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
  is_hidden           BOOLEAN       NOT NULL DEFAULT FALSE,
  PRIMARY KEY (order_id)
);

CREATE INDEX ui_phone_id_index ON ridehistory.user_index(phone_id, order_created_at);
CREATE INDEX ui_user_uid_index ON ridehistory.user_index(user_uid, order_created_at);
CREATE INDEX ui_seen_unarchived_at_index ON ridehistory.user_index(seen_unarchived_at);


-- a table to cache hidden orders as one can't write to dynamic tables synchronously
CREATE TABLE ridehistory.hidden_orders
(
  order_id            VARCHAR       NOT NULL,
  phone_id            VARCHAR       NOT NULL,
  user_uid            VARCHAR       NOT NULL,
  order_created_at    TIMESTAMPTZ   NOT NULL,
  created_at          TIMESTAMPTZ   NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
  PRIMARY KEY (order_id)
);

CREATE INDEX ho_phone_id_index ON ridehistory.hidden_orders(phone_id, order_created_at);
CREATE INDEX ho_user_uid_index ON ridehistory.hidden_orders(user_uid, order_created_at);
CREATE INDEX ho_created_at_index ON ridehistory.hidden_orders(created_at);


-- VERSION 2

ALTER TABLE ridehistory.user_index ALTER COLUMN seen_unarchived_at SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE ridehistory.hidden_orders ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;


-- VERSION 3

ALTER TABLE ridehistory.user_index
  ADD payment_tech_type VARCHAR,
  ADD payment_method_id VARCHAR;

CREATE INDEX ui_payment_tech_index ON ridehistory.user_index(
  payment_tech_type,
  payment_method_id,
  order_created_at
);

ALTER TABLE ridehistory.hidden_orders
  ADD payment_tech_type VARCHAR,
  ADD payment_method_id VARCHAR;

CREATE INDEX ho_payment_tech_index ON ridehistory.hidden_orders(
  payment_tech_type,
  payment_method_id,
  order_created_at
);


-- VERSION 4

ALTER TABLE ridehistory.user_index
    ALTER COLUMN user_uid DROP NOT NULL;

ALTER TABLE ridehistory.hidden_orders
    ALTER COLUMN user_uid DROP NOT NULL;


-- VERSION 5

ALTER TABLE ridehistory.hidden_orders
    ALTER COLUMN order_created_at DROP NOT NULL;

CREATE INDEX ho_phone_id_index_v2 ON ridehistory.hidden_orders(phone_id);
CREATE INDEX ho_user_uid_index_v2 ON ridehistory.hidden_orders(user_uid);
CREATE INDEX ho_payment_tech_index_v2 ON ridehistory.hidden_orders(
  payment_tech_type,
  payment_method_id
);


-- VERSION 6

-- DROP INDEX ridehistory.ho_phone_id_index;
-- DROP INDEX ridehistory.ho_user_uid_index;
-- DROP INDEX ridehistory.ho_payment_tech_index;
--
-- ALTER TABLE ridehistory.hidden_orders
--     DROP COLUMN order_created_at;


-- VERSION 7

CREATE TABLE ridehistory.takeout_delete_yandex_uid
(
  yandex_uid            VARCHAR       NOT NULL,
  delete_to             TIMESTAMPTZ   NOT NULL,
  created_at            TIMESTAMPTZ   NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),

  PRIMARY KEY (yandex_uid)
);

CREATE TABLE ridehistory.takeout_delete_phone_id
(
  phone_id              VARCHAR       NOT NULL,
  delete_to             TIMESTAMPTZ   NOT NULL,
  created_at            TIMESTAMPTZ   NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),

  PRIMARY KEY (phone_id)
);

CREATE TABLE ridehistory.takeout_job_result
(
  request_id            VARCHAR       NOT NULL,
  result_json           JSONB,
  created_at            TIMESTAMPTZ   NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),

  PRIMARY KEY (request_id)
);
