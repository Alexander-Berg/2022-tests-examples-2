SELECT bte.create_payloads_partition(
    range_from := '2020-07-01 14:00',
    range_to := '2020-07-01  15:00',
    partition_postfix := '2020_070114_2020_070115'
);
SELECT bte.create_payloads_partition(
    range_from := '2020-07-01 15:00',
    range_to := '2020-07-01 16:00',
    partition_postfix := '2020_070115_2020_070116'
);
SELECT bte.create_payloads_partition(
    range_from := '2020-07-01 16:00',
    range_to := '2020-07-01 17:00',
    partition_postfix := '2020_070116_2020_070117'
);
