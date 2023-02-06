CREATE TABLE IF NOT EXISTS driver_login.by_phone_pd_id
  (
     phone_pd_id TEXT           NOT NULL PRIMARY KEY,
     shown_times SMALLINT       NOT NULL DEFAULT 0,
     modified_at TIMESTAMPTZ    NOT NULL DEFAULT NOW()
  );
