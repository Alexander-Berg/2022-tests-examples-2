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
  id            SERIAL    PRIMARY KEY,
  udid          TEXT      NOT NULL,
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
  udid          TEXT      NOT NULL,
  reward_code   TEXT      NOT NULL,

  progress       INTEGER   NOT NULL,
  updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

  FOREIGN KEY (reward_code) REFERENCES achievements_pg.rewards (code)
);
CREATE UNIQUE INDEX progresses_idx ON achievements_pg.progresses (udid, reward_code);
CREATE INDEX progresses_updated_at_idx ON achievements_pg.progresses (updated_at);

-- helper type, used to in /seen handle
CREATE TYPE achievements_pg.seen_reward_v1 AS (
     code TEXT,
     level INTEGER
);
