CREATE SCHEMA drivers_status_ranges;

CREATE TABLE drivers_status_ranges.status_ranges(
  clid_uuid VARCHAR(80) NOT NULL,
  range_begin TIMESTAMP NOT NULL,
  range_end TIMESTAMP NOT NULL,
  status VARCHAR(10) NOT NULL,
  license_id VARCHAR(30) NOT NULL,
  license_country varchar(5)
);


CREATE INDEX status_ranges_clid_uuid ON drivers_status_ranges.status_ranges (clid_uuid);
CREATE INDEX status_ranges_range_begin ON drivers_status_ranges.status_ranges (range_begin);
CREATE INDEX status_ranges_range_end ON drivers_status_ranges.status_ranges (range_end);
