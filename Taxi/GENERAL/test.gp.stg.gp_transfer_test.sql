create table stg.gp_transfer_test
(
  col1 int8,
  col2 varchar
)
distributed by (col1);
