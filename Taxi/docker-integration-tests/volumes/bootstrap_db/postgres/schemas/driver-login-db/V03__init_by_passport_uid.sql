CREATE TABLE IF NOT EXISTS driver_login.by_passport_uid
  (
     passport_uid TEXT               NOT NULL PRIMARY KEY,
     eula_accepted_at TIMESTAMPTZ    NOT NULL, -- timestamp of Yandex.Pro EULA acceptance
     modified_at TIMESTAMPTZ         NOT NULL DEFAULT NOW()
  );
