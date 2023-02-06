CREATE SCHEMA edc_app_organizations;

SET SEARCH_PATH = edc_app_organizations;

CREATE TABLE organizations(
  id UUID NOT NULL PRIMARY KEY,
  name TEXT,
  city_id TEXT,
  address TEXT
);

CREATE INDEX organizations_name_idx ON organizations(name);
