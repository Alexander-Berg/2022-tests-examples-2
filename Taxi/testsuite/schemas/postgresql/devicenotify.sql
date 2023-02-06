/* V1 */

CREATE SCHEMA db;

CREATE TABLE db.version(
  db_0_1 INTEGER
);

CREATE SCHEMA devicenotify;

-- enum: channel_type_t
-- strict list of known types of external services
-- new channels (like 'apns') would be appended
CREATE TYPE devicenotify.channel_type_t AS ENUM (
  'fcm'
);

-- type: channel_t
-- contains external service tokens by channel types
-- e.g. ('fcm','Server-key-from-firebase-console')
CREATE TYPE devicenotify.channel_t AS (
  channel_type devicenotify.channel_type_t,
  token text
);


-- table: Users
-- contains mappings from taxi uid-s to postgres internal user_id
CREATE TABLE devicenotify.users(
  user_id serial NOT NULL UNIQUE,
  uid text NOT NULL,
  updated timestamp NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(user_id)
);

-- all uid-s must be unique
CREATE UNIQUE INDEX users_uid_idx ON devicenotify.users (uid);
-- we should be able to drop inactive users
CREATE INDEX users_updated_idx ON devicenotify.users (updated);


-- table: Services
-- contains mappings from taxi service names (e.g. 'taximeter')
-- to postgres internal service_id
CREATE TABLE devicenotify.services(
  service_id smallserial NOT NULL UNIQUE,
  name text NOT NULL,
  updated timestamp NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(service_id)
);

-- all service names must be unique
CREATE UNIQUE INDEX services_name_idx ON devicenotify.services (name);
-- monitor date of the last request from the service
CREATE INDEX services_updated_idx ON devicenotify.services (updated);


-- table: Tokens
-- each user may have one device per channel type,
-- so we store here no more than one active device for
-- each type from channel_type_t
CREATE TABLE devicenotify.tokens(
  user_id  integer NOT NULL REFERENCES devicenotify.users,
  channel_type devicenotify.channel_type_t NOT NULL,
  token text NOT NULL,
  updated timestamp NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(user_id, channel_type)
);

-- we should be able to unsubscribe inactive devices
CREATE INDEX tokens_updated_idx ON devicenotify.tokens (updated);

-- table: Topics
-- each service may subscribe a user to certain topics
-- this is atomic operation, so topics[] are stored here as array
-- several services may subscribe the same user to any topic
CREATE TABLE devicenotify.topics(
  user_id integer NOT NULL REFERENCES devicenotify.users,
  service_id smallint NOT NULL REFERENCES devicenotify.services,
  topics text[],
  updated timestamp NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(user_id, service_id)
);

-- we should be able to monitor inactive subscriptions
CREATE INDEX topics_updated_idx ON devicenotify.topics (updated);


-- table: Fallback_Queue
-- on problems with external push service we store here this request
-- if push was sent to topics[], which are usually a few, they are stored here
-- if push was addressed to bulk of users, their id-s are stored
-- in the complementary table fallback_queue_users, because they (user tokens)
-- would be processed portionwise
CREATE TABLE devicenotify.fallback_queue(
  queue_id bigserial NOT NULL UNIQUE,
  priority smallint NOT NULL,
  created timestamp NOT NULL DEFAULT current_timestamp,
  ttl timestamp NOT NULL,
  service_id smallint NOT NULL REFERENCES devicenotify.services,
  event text NULL,
  topics text[],
  payload text NOT NULL,
  repack text NULL,
  attempted timestamp NULL,  -- next attempt time
  PRIMARY KEY(queue_id)
);

-- process newest messages first
CREATE INDEX fallback_queue_created_idx ON devicenotify.fallback_queue (created DESC);
-- erase expired messages
CREATE INDEX fallback_queue_ttl_idx ON devicenotify.fallback_queue (ttl);

-- table: Fallback_Queue_Users
-- complementary table for Fallback_Queue
-- contains list of users we should send the message
-- for each queue_id there may be thousands of user_id-s
CREATE TABLE devicenotify.fallback_queue_users(
  queue_id bigint NOT NULL REFERENCES devicenotify.fallback_queue ON DELETE CASCADE,
  user_id integer NOT NULL REFERENCES devicenotify.users ON DELETE CASCADE,
  PRIMARY KEY(queue_id, user_id)
);




/* V2 */

ALTER TABLE db.version RENAME COLUMN db_0_1 TO db_0_2;

CREATE TYPE devicenotify.subscribe_action_t AS ENUM (
  'register',
  'revoke'
);

CREATE TABLE devicenotify.subscribe_queue(
  id bigserial NOT NULL UNIQUE,
  user_id integer NOT NULL REFERENCES devicenotify.users ON DELETE CASCADE,
  action devicenotify.subscribe_action_t NOT NULL,
  channel_type devicenotify.channel_type_t NOT NULL,
  token text NOT NULL,
  topic text NOT NULL,
  updated timestamp NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(id)
);

CREATE INDEX subscribe_queue_user_id_idx ON devicenotify.subscribe_queue (user_id);
CREATE INDEX subscribe_queue_updated_idx ON devicenotify.subscribe_queue (updated DESC);




/* V3 */

ALTER TABLE db.version RENAME COLUMN db_0_2 TO db_0_3;

ALTER TABLE devicenotify.users ALTER updated TYPE timestamptz USING updated AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.services ALTER updated TYPE timestamptz USING updated AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.tokens ALTER updated TYPE timestamptz USING updated AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.topics ALTER updated TYPE timestamptz USING updated AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.subscribe_queue ALTER updated TYPE timestamptz USING updated AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.fallback_queue ALTER created TYPE timestamptz USING created AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.fallback_queue ALTER ttl TYPE timestamptz USING ttl AT TIME ZONE 'UTC';

ALTER TABLE devicenotify.fallback_queue ALTER attempted TYPE timestamptz USING attempted AT TIME ZONE 'UTC';
