CREATE TYPE api_proxy.test_status_t AS ENUM (
  'ready',
  'running',
  'success',
  'failure',
  'cancelled'
  );

CREATE TABLE api_proxy.test_runs
(
  test_run_id   BIGINT                  NOT NULL,
  draft         TEXT                    NOT NULL,
  created       TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
  updated       TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
  finished      TIMESTAMPTZ,
  status        api_proxy.test_status_t NOT NULL,
  link_to_mds   TEXT,

  PRIMARY KEY(test_run_id)
);
