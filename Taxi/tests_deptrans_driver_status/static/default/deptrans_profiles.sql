INSERT INTO deptrans.profiles 
(driver_license_pd_id, deptrans_pd_id, updated_ts, import_date, status, checking_deptrans_id)
VALUES
/* Новые водители: */
    /* проверка */
    ('driver_license_pd_id_2', '2', '2020-12-30 14:00:01', NULL, NULL, '2'),
/* Временные водители: */
    /* с import_date */
    ('driver_license_pd_id_5', '5', '2020-12-30 14:00:02', '2020-12-29 14:00:02', 'temporary', NULL),
    /* ЛНР+ДНР */
    ('DRdriver_license_pd_id_11', '11', '2020-12-30 14:00:09', '2020-12-29 14:00:02', 'temporary', NULL),
    ('LRdriver_license_pd_id_12', '12', '2020-12-30 14:00:10', '2020-12-29 14:00:02', 'temporary', NULL),
    ('LRdriver_license_pd_id_13', '13', '2020-12-30 14:00:11', '2020-12-29 14:00:02', 'temporary', NULL),
    ('driver_license_pd_id_14', '14', '2020-12-30 14:00:04', '2020-12-29 14:00:02', 'temporary', NULL),
    /* без import_date */
    ('driver_license_pd_id_3', '3', '2020-12-30 14:00:03', NULL, 'temporary', NULL),
    /* проверка */
    ('driver_license_pd_id_8', '8', '2020-12-30 14:00:04', NULL, 'temporary', 'some_id'),
/* Просроченные водители: */ 
    /* с import_date */
    ('driver_license_pd_id_7', '7', '2020-12-30 14:00:05', '2019-12-29 14:00:05', 'temporary_outdated', NULL),
    /* без import_date */
    ('driver_license_pd_id_9', '9', '2020-12-30 14:00:06', NULL, 'temporary_outdated', NULL),
/* Постоянные водители: */
    ('driver_license_pd_id_1', '1', '2020-12-30 14:00:08', NULL, 'approved', NULL);

