INSERT INTO yt.kis_art_summary_report(park_id,
                                      report_date,
                                      active_drivers_count,
                                      drivers_with_permanent_id_count,
                                      drivers_with_temporary_id_count,
                                      drivers_with_requested_id_count,
                                      drivers_with_failed_id_count,
                                      drivers_without_id_count)
VALUES
    /* Here insert in reverse order to ensure
       that PK doesn't used for sorting */
    ('pid1', '2020-01-05'::DATE, 100, 31, 30, 30, 2, 7),
    ('pid1', '2020-01-04'::DATE, 200, 33, 30, 15, 15, 107),
    ('pid1', '2020-01-03'::DATE, 200, 33, 30, 30, 0, 107),
    ('pid1', '2020-01-02'::DATE, 200, 33, 20, 30, 10, 107),
    ('pid1', '2020-01-01'::DATE, 200, 33, 30, 30, 0, 107),

    ('pid2', '2020-01-05'::DATE, 400, 33, 30, 30, 0, 7),
    ('pid2', '2020-01-04'::DATE, 400, 33, 30, 30, 0, 107),
    ('pid2', '2020-01-03'::DATE, 400, 33, 30, 30, 0, 107),
    ('pid2', '2020-01-02'::DATE, 400, 33, 30, 30, 0, 107),
    ('pid2', '2020-01-01'::DATE, 400, 33, 30, 30, 0, 107)
;
