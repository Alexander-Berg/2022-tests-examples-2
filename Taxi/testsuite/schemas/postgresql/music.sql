CREATE SCHEMA music;

CREATE TABLE music.players
(
  order_id     TEXT        NOT NULL,
  alias_id     TEXT        NOT NULL UNIQUE,
  driver_id    TEXT        NOT NULL,
  user_id      TEXT        NULL,
  user_uid     TEXT        NOT NULL,
  created      TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
  version      INTEGER     NOT NULL DEFAULT 0,
  player_state JSONB       NULL,
  PRIMARY KEY (order_id)
);

CREATE INDEX players_alias_id ON music.players (alias_id);
CREATE INDEX players_driver_id ON music.players (driver_id);
CREATE INDEX players_user_uid ON music.players (user_uid);
CREATE INDEX players_created ON music.players (created);

CREATE TABLE music.player_actions
(
  action_id   TEXT        NOT NULL,
  action_code TEXT        NOT NULL,
  action_time TIMESTAMPTZ NOT NULL,
  action_data JSONB       NULL,

  order_id    TEXT REFERENCES music.players (order_id) ON DELETE CASCADE,
  alias_id    TEXT REFERENCES music.players (alias_id) ON DELETE CASCADE,

  PRIMARY KEY (order_id, action_id)
);

CREATE INDEX player_actions_alias_id ON music.player_actions (alias_id);
