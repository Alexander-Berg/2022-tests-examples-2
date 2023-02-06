CREATE EXTENSION postgis;

CREATE OR REPLACE FUNCTION unnest_multidim(ANYARRAY, OUT a ANYARRAY)
  RETURNS SETOF ANYARRAY AS
$func$
BEGIN
   IF $1 IS NULL OR cardinality($1) = 0 THEN
      RETURN;
   END IF;

   FOREACH a SLICE 1 IN ARRAY $1 LOOP
      RETURN NEXT;
   END LOOP;
END
$func$
LANGUAGE plpgsql IMMUTABLE;


CREATE TABLE services (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE channels (
  id          SERIAL NOT NULL PRIMARY KEY,
  name        VARCHAR(200) NOT NULL,  -- without UNIQUE, because of different services may create channels with the same name
  service_id  INTEGER NOT NULL REFERENCES services(id),
  etag        UUID NOT NULL,
  updated     TIMESTAMP WITH TIME ZONE NOT NULL,
  UNIQUE (service_id, name)
);

CREATE TABLE tags (
  id          SERIAL NOT NULL,
  name        TEXT,
  service_id  INTEGER NOT NULL REFERENCES services(id),

  UNIQUE (service_id, id),
  UNIQUE (service_id, name)
);

CREATE TABLE feeds (
  feed_id       UUID PRIMARY KEY,
  parent_feed_id UUID,
  service_id    INTEGER NOT NULL REFERENCES services(id),
  package_id    VARCHAR(200),
  request_id    VARCHAR(200),
  created       TIMESTAMP WITH TIME ZONE NOT NULL,
  expire        TIMESTAMP WITH TIME ZONE,
  payload       JSONB NOT NULL,
  publish_at    TIMESTAMP WITH TIME ZONE NOT NULL,
  token         TEXT,
  tags          INTEGER[],
  geo           GEOGRAPHY,
  geo_location  JSONB

);

CREATE INDEX feeds_created_index ON feeds (created DESC);

CREATE INDEX feeds_publish_index ON feeds (publish_at DESC);

CREATE INDEX feeds_expire_index ON feeds (expire DESC);

CREATE INDEX feeds_geo_index ON feeds USING GIST (geo);

CREATE TYPE publication_status AS ENUM ('published', 'read', 'viewed', 'removed');

CREATE TABLE feed_channel_status (
  feed_id     UUID NOT NULL REFERENCES feeds(feed_id),
  channel_id  INTEGER NOT NULL REFERENCES channels(id),
  created     TIMESTAMP WITH TIME ZONE NOT NULL,
  expire      TIMESTAMP WITH TIME ZONE,
  status      publication_status NOT NULL,
  meta        JSONB,
  PRIMARY KEY(feed_id, channel_id)
);

CREATE INDEX feed_channel_status_channel_id_status_index
  ON feed_channel_status (channel_id, status);

CREATE TABLE remove_requests (
  service_id  INTEGER NOT NULL REFERENCES services(id),
  request_id  VARCHAR(200),
  created     TIMESTAMP WITH TIME ZONE NOT NULL,

  UNIQUE (service_id, request_id)
);

CREATE TABLE distlocks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE idempotency_token (
  service_id            INTEGER NOT NULL REFERENCES services(id),
  idempotency_token     TEXT NOT NULL,
  created               TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY(service_id, idempotency_token)
);

CREATE TABLE feeds_statistics (
    request_id     VARCHAR(200) NOT NULL,
    service_id     INTEGER REFERENCES services(id),
    meta_counters  JSONB,
    updated        TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(service_id, request_id)
);

CREATE TABLE media (
    media_id          TEXT NOT NULL,
    media_type        TEXT NOT NULL,
    storage_type      TEXT NOT NULL,
    storage_settings  JSONB NOT NULL,
    updated           TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY(media_id)
);

CREATE TABLE remove_requests_by_request_id (
     service_id  INTEGER REFERENCES services(id),
     request_id  VARCHAR(200) NOT NULL,
     channels    VARCHAR(200)[],
     max_created TIMESTAMP WITH TIME ZONE NOT NULL,
     recursive   boolean NOT NULL,
     created TIMESTAMP WITH TIME ZONE NOT NULL,

     UNIQUE (service_id, request_id, max_created)
);

CREATE TYPE payload_param AS (
    key       TEXT,
    value     TEXT
);

CREATE TYPE feed_payload_row AS (
    feed_id            UUID,
    channel_id         BIGINT,
    payload_overrides  JSONB,
    payload_params     payload_param[]
);

CREATE TABLE feed_payload (
      feed_id            UUID NOT NULL REFERENCES feeds(feed_id),
      channel_id         INTEGER NOT NULL REFERENCES channels(id),
      payload_overrides  JSONB,
      payload_params     payload_param[],
      PRIMARY KEY(feed_id, channel_id)
);

CREATE TYPE cluster_type AS ENUM ('general', 'meta');

CREATE TABLE geo_clusters (
      cluster_id UUID         NOT NULL,
      zoom_level INTEGER      NOT NULL,
      type       cluster_type NOT NULL,
      geo        GEOGRAPHY, -- тут хранится bbox, для мета классов NULL
      PRIMARY KEY (cluster_id)
);

CREATE TABLE geo_markers (
     marker_id   UUID      NOT NULL,
     cluster_ids UUID[]    NOT NULL,
     feed_id     UUID      NOT NULL REFERENCES feeds (feed_id),
     priority    INTEGER   NOT NULL,
     meta        JSONB,
     geo         GEOGRAPHY NOT NULL,
     lon         REAL,
     lat         REAL,
     PRIMARY KEY (marker_id)
);

CREATE INDEX IF NOT EXISTS geo_markers_index
    ON geo_markers
    USING GIST (geo);

CREATE INDEX IF NOT EXISTS geo_clusters_index
    ON geo_clusters
    USING GIST (geo)
    WHERE geo IS NOT NULL;

CREATE INDEX geo_markers_gin_index
    ON geo_markers
    USING GIN(cluster_ids);

CREATE INDEX geo_clusters_zoom_level_index
    ON geo_clusters(zoom_level)
    WHERE type = 'meta';
