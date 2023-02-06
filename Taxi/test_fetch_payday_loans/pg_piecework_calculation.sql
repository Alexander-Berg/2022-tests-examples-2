INSERT INTO piecework.payday_employee_loan (
  employee_id, company_id, date_time, loan_id, amount, paid_at, period
) VALUES (
  'ivanov_uid', 'some_id', '2022-02-05 15:00:00', 'loan_id_1', 500.0,
  '2022-02-05 15:00:05', '2022-02-01'
), (
  'petrov_uid', 'some_id', '2022-02-01 00:00:00', 'loan_id_2', 300.0,
  '2022-02-01 00:00:05', '2022-01-01'
), (
  'smornov_uid', 'some_id', '2022-01-31 23:59:59', 'loan_id_3', 100.0,
  '2022-02-01 00:00:05', '2022-02-01'
);
INSERT INTO piecework.mapping_payday_uid_login (login, payday_uid) VALUES
('ivanov', 'ivanov_uid'),
('petrov', 'petrov_uid'),
('smirnov', 'smirnov_uid');
