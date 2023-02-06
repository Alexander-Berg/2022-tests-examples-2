CREATE SCHEMA achievements_pg;

-- types of rewards
CREATE TABLE achievements_pg.rewards
(
  id         SERIAL   PRIMARY KEY,

-- human-readable slug
  code       TEXT     UNIQUE NOT NULL,

-- internal name
  admin_name TEXT,

  author     TEXT,
  category   TEXT,
  updated_at    TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
  created_at    TIMESTAMPTZ    NOT NULL DEFAULT NOW(),

-- some achievements can be seen in 'locked' state.
-- others can only be seen after they have become 'unlocked'.
  has_locked_state BOOL NOT NULL DEFAULT FALSE,

  is_leveled BOOL NOT NULL DEFAULT FALSE,
  has_progress BOOL NOT NULL DEFAULT FALSE,
  levels INTEGER[] NOT NULL DEFAULT '{}'
);
CREATE INDEX rewards_updated_at_idx ON achievements_pg.rewards (updated_at);

-- rewards by driver
CREATE TABLE achievements_pg.driver_rewards
(
  id          SERIAL    PRIMARY KEY,
  udid        TEXT      NOT NULL,
  reward_code   TEXT      NOT NULL,

  -- level `0` means that this reward is visible, but still locked
  level       INTEGER   NOT NULL,

  updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

  -- when this achievement has become unlocked (level 0 -> 1) for the first time
  unlocked_at TIMESTAMPTZ,

  -- when user has seen this achievement as "new unlocked" for the first time
  seen_at     TIMESTAMPTZ,

  FOREIGN KEY (reward_code) REFERENCES achievements_pg.rewards (code)
);
CREATE UNIQUE INDEX driver_rewards_idx ON achievements_pg.driver_rewards (udid, reward_code, level);
CREATE INDEX driver_rewards_updated_at_idx ON achievements_pg.driver_rewards (updated_at);

-- progresses by driver
CREATE TABLE achievements_pg.progresses
(
  udid        TEXT      NOT NULL,
  reward_code   TEXT      NOT NULL,

  progress       INTEGER   NOT NULL,
  updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

  FOREIGN KEY (reward_code) REFERENCES achievements_pg.rewards (code)
);
CREATE UNIQUE INDEX progresses_idx ON achievements_pg.progresses (udid, reward_code);
CREATE INDEX progresses_updated_at_idx ON achievements_pg.progresses (updated_at);


 -- schedule to run uploads periodically
CREATE TABLE achievements_pg.uploads_schedule
(
  id            TEXT PRIMARY KEY,

-- each upload knows, which reward it assigns
  reward_code     TEXT NOT NULL,

-- uploads can have different types, not simply assign unlocked rewards to drivers
  upload_type   TEXT NOT NULL,

-- minutes
  period        INTEGER,

-- text of YQL-query, returning list of drivers
  yql           TEXT,

  author        TEXT,

-- if false, uploads for this schedule will not be started
  is_active     BOOLEAN NOT NULL,

  updated       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(reward_code, upload_type),
  FOREIGN KEY (reward_code) REFERENCES achievements_pg.rewards (code)
);
CREATE INDEX uploads_schedule_updated_idx ON achievements_pg.uploads_schedule (updated);

-- log of upload operations
CREATE TABLE achievements_pg.uploads
(
  id            SERIAL PRIMARY KEY,
  reward_code   TEXT NOT NULL,

-- new/pending/error/cancel/complete
  status        TEXT NOT NULL,

  yql           TEXT NOT NULL,
  upload_type   TEXT NOT NULL,
  author        TEXT,

-- results of YT operation
-- contain either operation_id, or list of errors
  results       JSONB,

-- can be NULL if upload was created manually
  schedule_id   TEXT,

  updated       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  FOREIGN KEY (reward_code) REFERENCES achievements_pg.rewards (code),
  FOREIGN KEY (schedule_id) REFERENCES achievements_pg.uploads_schedule(id)
);
