CREATE SCHEMA latvia_rides_reports;

CREATE TABLE latvia_rides_reports.reports (
    report_id text PRIMARY KEY,
    modified_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE latvia_rides_reports.order_income_events (
    entry_id bigint PRIMARY KEY,
    modified_at timestamptz NOT NULL DEFAULT now(),
    report_id text NOT NULL REFERENCES latvia_rides_reports.reports
);
