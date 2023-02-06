DROP SCHEMA IF EXISTS persey_payments CASCADE;

CREATE SCHEMA persey_payments;


-- VERSION 1


CREATE TABLE persey_payments.lab
(
  lab_id                         VARCHAR             NOT NULL,
  partner_uid                    VARCHAR,
  operator_uid                   VARCHAR,
  trust_product_id_delivery      VARCHAR,
  trust_product_id_test          VARCHAR,
  trust_partner_id               VARCHAR,
  balance_client_id              VARCHAR,
  balance_client_person_id       VARCHAR,
  balance_contract_id            VARCHAR,
  status                         VARCHAR             NOT NULL DEFAULT 'create_attempt',
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (lab_id)
);

CREATE TABLE persey_payments.order
(
  order_id                       VARCHAR             NOT NULL,
  payment_method_id              VARCHAR             NOT NULL,
  purchase_token                 VARCHAR,
  trust_payment_id               VARCHAR,
  trust_order_id_delivery        VARCHAR,
  trust_order_id_test            VARCHAR,
  status                         VARCHAR,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (order_id)
);

CREATE TABLE persey_payments.fund
(
  fund_id                        VARCHAR             NOT NULL,
  name                           VARCHAR             NOT NULL,
  offer_link                     VARCHAR             NOT NULL,
  operator_uid                   VARCHAR             NOT NULL,
  balance_client_id              VARCHAR             NOT NULL,
  trust_partner_id               VARCHAR             NOT NULL,
  trust_product_id               VARCHAR             NOT NULL,
  is_hidden                      BOOLEAN             NOT NULL DEFAULT FALSE,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (fund_id)
);

CREATE TABLE persey_payments.donation
(
  id                             SERIAL              NOT NULL,
  fund_id                        VARCHAR             NOT NULL REFERENCES persey_payments.fund (fund_id),
  yandex_uid                     VARCHAR,
  sum                            VARCHAR             NOT NULL,
  user_name                      VARCHAR             NOT NULL,
  user_email                     VARCHAR             NOT NULL,
  purchase_token                 VARCHAR             NOT NULL,
  trust_order_id                 VARCHAR             NOT NULL,
  status                         VARCHAR             NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);


-- VERSION 2


DROP TABLE IF EXISTS persey_payments.basket;
DROP TABLE IF EXISTS persey_payments.order;

CREATE TABLE persey_payments.order
(
  order_id                       VARCHAR             NOT NULL,
  payment_method_id              VARCHAR,
  need_free                      BOOLEAN             NOT NULL,
  status                         VARCHAR             NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (order_id)
);

CREATE TABLE persey_payments.basket
(
  purchase_token                 VARCHAR,
  order_id                       VARCHAR             NOT NULL REFERENCES persey_payments.order (order_id),
  mark                           VARCHAR             NOT NULL,
  test_cost                      VARCHAR             NOT NULL,
  delivery_cost                  VARCHAR             NOT NULL,
  sampling_cost                  VARCHAR,
  fund_id                        VARCHAR             REFERENCES persey_payments.fund (fund_id),
  trust_payment_id               VARCHAR,
  trust_order_id_test            VARCHAR,
  trust_order_id_delivery        VARCHAR,
  hold_amount                    DECIMAL(20, 4)      NOT NULL DEFAULT '0',
  user_uid                       VARCHAR             NOT NULL,
  status                         VARCHAR             NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (order_id, mark)
);


-- VERSION 3


ALTER TABLE persey_payments.fund ADD available_amount DECIMAL(20, 4) NOT NULL DEFAULT '0';

CREATE TABLE persey_payments.fund_booking
(
  order_id                       VARCHAR             NOT NULL REFERENCES persey_payments.order (order_id),
  mark                           VARCHAR             NOT NULL,
  fund_id                        VARCHAR             NOT NULL REFERENCES persey_payments.fund (fund_id),
  amount                         DECIMAL(20, 4)      NOT NULL,
  book_till                      TIMESTAMPTZ         NOT NULL,

  PRIMARY KEY (order_id, mark)
);

CREATE TABLE persey_payments.refund
(
  order_id                       VARCHAR             NOT NULL REFERENCES persey_payments.order (order_id),
  mark                           VARCHAR             NOT NULL,
  refund_id                      VARCHAR             NOT NULL,
  trust_refund_id                VARCHAR             NOT NULL,
  operator_login                 VARCHAR             NOT NULL,
  ticket                         VARCHAR             NOT NULL,

  PRIMARY KEY (order_id, mark, refund_id)
);


-- VERSION 4


ALTER TABLE persey_payments.donation
    ALTER user_name DROP NOT NULL,
    ALTER user_email DROP NOT NULL;


-- VERSION 5


ALTER TABLE persey_payments.basket
    ADD payout_ready_dt TIMESTAMPTZ;


-- VERSION 6


ALTER TABLE persey_payments.donation
    ADD city                     VARCHAR             DEFAULT NULL,
    ADD category                 VARCHAR             DEFAULT NULL,
    ADD partner_name             VARCHAR             DEFAULT NULL;


-- VERSION 7


CREATE TABLE persey_payments.subs_product
(
  id                             SERIAL              NOT NULL,
  amount                         VARCHAR             NOT NULL,
  period                         VARCHAR             NOT NULL,
  retry_charging_limit           VARCHAR             NOT NULL,
  retry_charging_delay           VARCHAR             NOT NULL,
  trust_product_id               VARCHAR             NOT NULL,

  PRIMARY KEY (id),
  UNIQUE (amount, period, retry_charging_limit, retry_charging_delay)
);

CREATE TABLE persey_payments.subs
(
  id                             SERIAL              NOT NULL,
  external_id                    VARCHAR             NOT NULL,
  subs_product_id                INTEGER             NOT NULL REFERENCES persey_payments.subs_product (id),
  fund_id                        VARCHAR             NOT NULL REFERENCES persey_payments.fund (fund_id),
  yandex_uid                     VARCHAR,
  user_name                      VARCHAR             NOT NULL,
  user_email                     VARCHAR             NOT NULL,
  trust_order_id                 VARCHAR             NOT NULL,
  city                           VARCHAR,
  category                       VARCHAR,
  partner_name                   VARCHAR,
  status                         VARCHAR             NOT NULL,
  subs_until_ts                  TIMESTAMPTZ,
  hold_until_ts                  TIMESTAMPTZ,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE INDEX subs_external_id_index ON persey_payments.subs(external_id);

CREATE TABLE persey_payments.charge_warnings
(
  id                             SERIAL              NOT NULL,
  subs_id                        INTEGER             NOT NULL REFERENCES persey_payments.subs (id),
  subs_until_ts                  TIMESTAMPTZ         NOT NULL,

  PRIMARY KEY (id),
  UNIQUE (subs_id, subs_until_ts)
);

ALTER TABLE persey_payments.donation
    ADD subs_id INTEGER DEFAULT NULL;


-- VERSION 8


ALTER TABLE persey_payments.fund
    ADD exclude_from_sampling BOOLEAN NOT NULL DEFAULT FALSE;


-- VERSION 9


ALTER TABLE persey_payments.subs
    ALTER user_name DROP NOT NULL;


-- VERSION 10


CREATE TABLE persey_payments.ride_subs
(
  id                             SERIAL              NOT NULL,
  yandex_uid                     VARCHAR             NOT NULL,
  phone_id                       VARCHAR             NOT NULL,
  brand                          VARCHAR             NOT NULL,
  fund_id                        VARCHAR             NOT NULL REFERENCES persey_payments.fund (fund_id),
  mod                            INTEGER             NOT NULL,
  city                           VARCHAR,
  category                       VARCHAR,
  partner_name                   VARCHAR,
  parent_ride_subs_id            INTEGER             REFERENCES persey_payments.ride_subs (id),
  locale                         VARCHAR             NOT NULL,
  hidden_at                      TIMESTAMPTZ,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE TABLE persey_payments.active_ride_subs
(
  id                             SERIAL              NOT NULL,
  ride_subs_id                   INTEGER             NOT NULL REFERENCES persey_payments.ride_subs (id),
  yandex_uid                     VARCHAR             NOT NULL,
  brand                          VARCHAR             NOT NULL,

  PRIMARY KEY (id),
  UNIQUE (yandex_uid, brand)
);

CREATE TABLE persey_payments.supporter
(
  id                             SERIAL              NOT NULL,
  ride_subs_amount               DECIMAL             NOT NULL DEFAULT '0',
  subs_amount                    DECIMAL             NOT NULL DEFAULT '0',
  oneshot_amount                 DECIMAL             NOT NULL DEFAULT '0',
  has_contribution               BOOLEAN             NOT NULL DEFAULT FALSE,
  current_subs_num               INTEGER             NOT NULL DEFAULT 0,
  current_ride_subs              BOOLEAN             NOT NULL DEFAULT FALSE,

  PRIMARY KEY (id)
);

CREATE INDEX supporter_subs_num_index ON persey_payments.supporter(current_subs_num);
CREATE INDEX supporter_ride_subs_index ON persey_payments.supporter(current_ride_subs);

CREATE TABLE persey_payments.supporter_uid
(
  id                             SERIAL              NOT NULL,
  supporter_id                   INTEGER             NOT NULL REFERENCES persey_payments.supporter (id),
  yandex_uid                     VARCHAR             NOT NULL,

  PRIMARY KEY (id),
  UNIQUE (yandex_uid)
);

CREATE INDEX supporter_uid_supporter_index ON persey_payments.supporter_uid(supporter_id);

CREATE TABLE persey_payments.supporter_email
(
  id                             SERIAL              NOT NULL,
  supporter_id                   INTEGER             NOT NULL REFERENCES persey_payments.supporter (id),
  user_email                     VARCHAR             NOT NULL,

  PRIMARY KEY (id),
  UNIQUE (user_email)
);

CREATE INDEX supporter_email_supporter_index ON persey_payments.supporter_email(supporter_id);

CREATE TABLE persey_payments.seen_bound_uids
(
  id                             SERIAL              NOT NULL,
  portal_yandex_uid              VARCHAR             NOT NULL,
  phonish_yandex_uid             VARCHAR             NOT NULL,

  PRIMARY KEY (id),
  UNIQUE(portal_yandex_uid, phonish_yandex_uid)
);

CREATE TABLE persey_payments.stuck_donation
(
  id                             SERIAL              NOT NULL,
  donation_id                    INTEGER             NOT NULL REFERENCES persey_payments.donation (id),

  PRIMARY KEY (id)
);

CREATE TABLE persey_payments.ride_subs_event
(
  id                             SERIAL              NOT NULL,
  ride_subs_id                   INTEGER             NOT NULL REFERENCES persey_payments.ride_subs (id),
  type                           VARCHAR             NOT NULL,
  payload                        VARCHAR,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE TABLE persey_payments.subs_event
(
  id                             SERIAL              NOT NULL,
  subs_id                        INTEGER             NOT NULL REFERENCES persey_payments.subs (id),
  type                           VARCHAR             NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id),
  UNIQUE(subs_id, type)
);

CREATE TABLE persey_payments.donation_stats_job
(
  id                             SERIAL              NOT NULL,
  last_donation_id               INTEGER             REFERENCES persey_payments.donation (id),
  last_subs_event_id             INTEGER             REFERENCES persey_payments.subs_event (id),
  last_ride_subs_event_id        INTEGER             REFERENCES persey_payments.ride_subs_event (id),
  finished_at                    TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE INDEX ride_subs_event_subs_index ON persey_payments.ride_subs_event(ride_subs_id, id);

CREATE TABLE persey_payments.ride_subs_event_ptr
(
  id                             SERIAL              NOT NULL,
  ride_subs_id                   INTEGER             NOT NULL REFERENCES persey_payments.ride_subs (id),
  event_id                       INTEGER             NOT NULL REFERENCES persey_payments.ride_subs_event (id),

  PRIMARY KEY (id),
  UNIQUE (ride_subs_id)
);

ALTER TABLE persey_payments.donation
    ADD ride_subs_id             INTEGER             REFERENCES persey_payments.ride_subs (id),
    ADD order_id                 VARCHAR,
    ADD updated_at               TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD UNIQUE (order_id),
    ALTER purchase_token         DROP NOT NULL,
    ALTER trust_order_id         DROP NOT NULL;

CREATE INDEX donation_updated_at_index ON persey_payments.donation(updated_at);

CREATE OR REPLACE FUNCTION set_updated() RETURNS TRIGGER AS $set_updated$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated BEFORE UPDATE ON persey_payments.donation
FOR EACH ROW EXECUTE PROCEDURE set_updated();

CREATE TABLE persey_payments.ride_subs_order_user
(
  id                             SERIAL              NOT NULL,
  yandex_uid                     VARCHAR             NOT NULL,
  brand                          VARCHAR             NOT NULL,
  order_id                       VARCHAR             NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE INDEX ride_subs_order_user_user_index ON persey_payments.ride_subs_order_user(yandex_uid, brand);
CREATE INDEX ride_subs_order_user_created_at_index ON persey_payments.ride_subs_order_user(created_at);

CREATE TABLE persey_payments.ride_subs_order_cache
(
  id                             SERIAL              NOT NULL,
  order_id                       VARCHAR             NOT NULL,
  mod                            INTEGER,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE INDEX ride_subs_order_cache_created_at_index ON persey_payments.ride_subs_order_cache(created_at);


-- VERSION 11

ALTER TABLE persey_payments.supporter
    DROP current_ride_subs,
    ADD current_ride_subs_num    INTEGER             NOT NULL DEFAULT 0;

CREATE INDEX supporter_ride_subs_num_index ON persey_payments.supporter(current_ride_subs_num);


-- VERSION 12

ALTER TABLE persey_payments.subs
    ADD updated_at               TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX subs_updated_at_index ON persey_payments.subs(updated_at);

CREATE TRIGGER set_updated BEFORE UPDATE ON persey_payments.subs
FOR EACH ROW EXECUTE PROCEDURE set_updated();


ALTER TABLE persey_payments.ride_subs
    ADD updated_at               TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX ride_subs_updated_at_index ON persey_payments.ride_subs(updated_at);

CREATE TRIGGER set_updated BEFORE UPDATE ON persey_payments.ride_subs
FOR EACH ROW EXECUTE PROCEDURE set_updated();


ALTER TABLE persey_payments.supporter_uid
    ADD updated_at               TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX supporter_uid_updated_at_index ON persey_payments.supporter_uid(updated_at);

CREATE TRIGGER set_updated BEFORE UPDATE ON persey_payments.supporter_uid
FOR EACH ROW EXECUTE PROCEDURE set_updated();


-- VERSION 13

CREATE TABLE persey_payments.ride_subs_paid_order
(
  id                             SERIAL              NOT NULL,
  order_id                       VARCHAR             NOT NULL,
  amount                         DECIMAL(20, 4)      NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id)
);

CREATE INDEX ride_subs_paid_order_created_at_index ON persey_payments.ride_subs_paid_order(created_at);

ALTER TABLE persey_payments.fund
    ADD applepay_country_code    VARCHAR,
    ADD applepay_item_title      VARCHAR;

ALTER TABLE persey_payments.ride_subs_order_cache
    ADD fund_id                  VARCHAR             REFERENCES persey_payments.fund (fund_id);


-- VERSION 15

CREATE INDEX donation_yandex_uid_index ON persey_payments.donation(yandex_uid);

CREATE TABLE persey_payments.bound_uids
(
  id                             SERIAL              NOT NULL,
  portal_yandex_uid              VARCHAR             NOT NULL,
  phonish_yandex_uid             VARCHAR             NOT NULL,

  PRIMARY KEY (id),
  UNIQUE (phonish_yandex_uid)
);

DROP TABLE persey_payments.donation_stats_job;
DROP TABLE persey_payments.stuck_donation;
DROP TABLE persey_payments.seen_bound_uids;
DROP TABLE persey_payments.supporter_uid;
DROP TABLE persey_payments.supporter_email;
DROP TABLE persey_payments.supporter;


-- VERSION 16

ALTER TABLE persey_payments.donation
    ADD reject_newsletter        BOOLEAN;


-- VERSION 17

DROP TABLE persey_payments.ride_subs_event_ptr;


-- VERSION 18

ALTER TABLE persey_payments.donation
    ADD brand                    VARCHAR,
    ADD UNIQUE (brand, order_id);

ALTER TABLE persey_payments.ride_subs
    ALTER phone_id               DROP NOT NULL;


-- VERSION 19

ALTER TABLE persey_payments.donation
    DROP CONSTRAINT donation_order_id_key;


-- VERSION 20

CREATE VIEW persey_payments.rich_donation AS
    SELECT
        *,
        (
            CASE
                WHEN subs_id IS NOT NULL THEN 'subs'
                WHEN ride_subs_id IS NOT NULL THEN 'ride_subs'
                ELSE 'oneshot'
            END
        ) AS donation_type
    FROM persey_payments.donation;


-- VERSION 21

ALTER TABLE persey_payments.ride_subs
    ADD application              VARCHAR;


CREATE TABLE persey_payments.billing_event
(
  brand                          VARCHAR             NOT NULL,
  order_id                       VARCHAR             NOT NULL,
  event                          VARCHAR             NOT NULL,
  created_at                     TIMESTAMPTZ         NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (brand, order_id, event)
);


-- VERSION 22

ALTER SEQUENCE persey_payments.ride_subs_order_cache_id_seq AS BIGINT;
ALTER TABLE persey_payments.ride_subs_order_cache ALTER id TYPE BIGINT;

ALTER SEQUENCE persey_payments.ride_subs_order_user_id_seq AS BIGINT;
ALTER TABLE persey_payments.ride_subs_order_user ALTER id TYPE BIGINT;

ALTER TABLE persey_payments.bound_uids DROP id;


-- VERSION 23

CREATE INDEX donation_order_id_index ON persey_payments.donation(order_id);


-- VERSION 24

ALTER TABLE persey_payments.donation
    ADD application              VARCHAR;
ALTER TABLE persey_payments.ride_subs
    ADD subscription_source      VARCHAR;

-- VERSION 25

ALTER TABLE persey_payments.bound_uids
  ADD updated_at TIMESTAMPTZ;
ALTER TABLE persey_payments.bound_uids
  ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
CREATE TRIGGER set_updated BEFORE UPDATE ON persey_payments.bound_uids
  FOR EACH ROW EXECUTE PROCEDURE set_updated();

-- VERSION 26

ALTER TABLE persey_payments.bound_uids
  ALTER COLUMN updated_at SET NOT NULL;
CREATE INDEX CONCURRENTLY bound_uids_update_at_idx
  ON persey_payments.bound_uids(updated_at);

-- VERSION 27

ALTER TABLE persey_payments.subs_product
    ADD COLUMN shared BOOLEAN NOT NULL DEFAULT TRUE;
CREATE UNIQUE INDEX subs_product_compound_idx
    ON persey_payments.subs_product(
        amount,
        period,
        retry_charging_limit,
        retry_charging_delay
    ) WHERE shared = TRUE;

-- VERSION 28

ALTER TABLE persey_payments.subs_product
    DROP CONSTRAINT subs_product_amount_period_retry_charging_limit_retry_charg_key;

-- VERSION 29

ALTER TABLE persey_payments.subs
    ADD COLUMN application VARCHAR;
