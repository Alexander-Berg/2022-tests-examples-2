CREATE SCHEMA safety_center;

/* It appears that we ain't need domain anymore
   (because NOT NULL and DEFAULT constraints doesn't work properly with CREATE TYPE)
   but it is too difficult to get rid of it, so we left it here.
   It's usage is deprecated.
 */
CREATE DOMAIN text_deprecated AS TEXT DEFAULT '';

CREATE TYPE contact AS (
  name text_deprecated,
  personal_phone_id text_deprecated
);

CREATE TABLE safety_center.contacts (
  yandex_uid TEXT PRIMARY KEY,
  contacts contact [],
  created_at timestamptz NOT NULL,
  updated_at timestamptz
);

CREATE TABLE safety_center.accidents (
  accident_id TEXT PRIMARY KEY,
  idempotency_key TEXT UNIQUE NOT NULL,
  order_id TEXT NOT NULL,
  order_alias_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  yandex_uid TEXT DEFAULT '' NOT NULL,
  confidence INTEGER NOT NULL,
  occurred_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz DEFAULT NULL,
  confirmed BOOLEAN DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS order_id_key ON safety_center.accidents(order_id);

CREATE TABLE safety_center.sharing (
    sharing_id TEXT PRIMARY KEY,
    idempotency_key TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    yandex_uid TEXT NOT NULL,
    user_locale TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    recipients TEXT [] DEFAULT NULL,
    order_id TEXT DEFAULT NULL,
    coordinates point DEFAULT NULL,
    accuracy NUMERIC DEFAULT NULL,
    created_at timestamptz NOT NULL
);
