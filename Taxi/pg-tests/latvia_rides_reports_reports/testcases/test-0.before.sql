INSERT INTO latvia_rides_reports.reports
(report_id, modified_at)
VALUES
('report_id1', '2021-12-12T11:59:00.1234+03:00'::TIMESTAMPTZ),
('report_id2', '2010-12-12T11:59:00.1234+03:00'::TIMESTAMPTZ);

INSERT INTO latvia_rides_reports.order_income_events
(entry_id, modified_at, report_id)
VALUES
(1, '2021-12-12T11:59:00.1234+03:00'::TIMESTAMPTZ, 'report_id1');
