INSERT INTO yt.kis_art_detailed_report(park_id,
                                       report_date,
                                       driver_profile_id,
                                       kis_art_id,
                                       kis_art_status,
                                       driver_full_name)
VALUES
    ('pid1', '2020-01-04'::DATE, 'dr_pr_9', '', 'requested', 'Олексеев Кто-то Там'),
    ('pid1', '2020-01-05'::DATE, 'dr_pr_1', 'kis_art_id1', 'permanent', 'Фамилия Имя Отчество'),
    ('pid1', '2020-01-05'::DATE, 'dr_pr_18', 'kis_art_id18', 'permanent', 'Фамилия Имя Отчество'),
    ('pid1', '2020-01-04'::DATE, 'dr_pr_1', 'kis_art_id1', 'requested', 'Калинин Андрей Алексеевич'),
    ('pid1', '2020-01-04'::DATE, 'dr_pr_2', '', 'requested', 'Малышева Анна Сергеевна'),
    ('pid1', '2020-01-04'::DATE, 'dr_pr_8', 'bhbliubl', 'failed', 'Сергеев К Д'),
    ('pid1', '2020-01-04'::DATE, 'dr_pr_3', 'kis_art_id3', 'temporary', 'Фомин Александр Николаевич'),
    ('pid1', '2020-01-04'::DATE, 'dr_pr_4', 'kis_art_id4', 'without_id', 'Матвиенко Богдан Сергеевич'),
    ('pid2', '2020-01-04'::DATE, 'dr_pr_0', '', 'requested', 'Безвестный Старый Водитель'),
    ('pid2', '2020-01-04'::DATE, 'dr_pr_1', '', 'requested', 'Prosto testov'),
    ('pid1', '2020-01-04'::DATE, 'dr_pr_7', 'temporary_7', 'temporary', 'Михайлов Владимир Сергеевич'),
    ('pid2', '2020-01-04'::DATE, 'dr_pr_5', '', 'requested', 'gagaga Test'),
    ('pid3', '2020-12-12'::DATE, 'dr_pr_0', 'kis_art_id_3_0', 'permanent', ''),
    ('pid3', '2020-12-12'::DATE, 'dr_pr_1', 'kis_art_id_3_1', 'permanent', 'Алексеева Алина Юрьевна') 
;
