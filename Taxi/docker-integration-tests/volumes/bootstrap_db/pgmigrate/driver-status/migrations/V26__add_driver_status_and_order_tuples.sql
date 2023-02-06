CREATE TYPE ds.contractor_status_tuple AS (
  contractor_id BIGINT,
  status ds.status,
  source ds.source,
  updated_ts TIMESTAMP WITH TIME ZONE,
  flow_version ds.flow_version
);

CREATE TYPE ds.order_status_tuple AS (
 id VARCHAR(32),
 contractor_id BIGINT,
 status ds.order_status,
 provider_id SMALLINT,
 updated_ts TIMESTAMP WITH TIME ZONE
);

CREATE TYPE ds.contractor_update_tuple AS (
 contractor_id BIGINT,
 updated_ts TIMESTAMP WITH TIME ZONE
);
