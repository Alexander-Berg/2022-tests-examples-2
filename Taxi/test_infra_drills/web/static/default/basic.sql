INSERT INTO drills.anchormen(
    login, drills_count, last_drill_date
)
VALUES(
    'khomikki', 100, '2032-01-20'
);

INSERT INTO drills.anchormen(
    login, drills_count, last_drill_date
)
VALUES(
    'temox', 3, '2031-12-25'
);

INSERT INTO drills.anchormen(
    login, drills_count, last_drill_date
)
VALUES(
    'sgrebenyukov', 50, '2032-01-17'
);

INSERT INTO drills.tests(
    "key", "value"
) 
VALUES(
    'startrek', 'TAXIADMIN-102'
);

INSERT INTO drills.drill_events (
    event_id, event_state, start_ts, end_ts, summary, event_description
)
VALUES(123456, '', '2022-01-20T16:00:00', '2032-01-20T19:00:00', 'test summary', 'test description');

INSERT INTO drills.drill_announces (announce_count)
VALUES(1);

INSERT INTO drills.drill_cards(
    "state", announce_id, business_unit, drill_type, datacenter, drill_date, time_interval, coordinator, anchorman, members, calendar_event, comment, st_ticket, st_ticket_summary, st_ticket_description, updated_at, deleted_at
)
VALUES(
    'PLANNED', 1, 'taxi', 'external', 'IVA', '2032-01-20', '16:00 - 19:00', 'temox', 'temox', 'test1, test2', 123456, 'comment', 'TAXIADMIN-102', NULL, NULL, '2022-01-15', NULL
);

INSERT INTO drills.drill_announces (announce_count)
VALUES(1);

INSERT INTO drills.drill_cards(
    "state", announce_id, business_unit, drill_type, datacenter, drill_date, time_interval, coordinator, anchorman, members, calendar_event, comment, st_ticket, st_ticket_summary, st_ticket_description, updated_at, deleted_at
)
VALUES(
    'PLANNED', 2, 'taxi', 'maintenance', 'VLA', '2032-01-29', '16:00 - 19:00', 'temox', 'temox', 'test1', NULL, 'comment', 'TAXIADMIN-81', '[net] 2022-02-24 16:00 - 19:00 Учения в ДЦ VLA', '====Учения в ДЦ **VLA**%%(wacko wrapper=shade)Дата и время: 2022-02-24 **16:00 - 19:00**Цель: Подготовка к регламентным работамСпособ закрытия: **[net]** с предварительным снятием нагрузки%%====Для справки:- ((https://wiki.yandex-team.ru/taxi-ito/drillsreq/#osobennostiotkljuchenijadatacentrov Особенности отключения ДЦ))- ((https://wiki.yandex-team.ru/taxi-ito/drillsreq Регламент учений))====**Координатор:** https://staff.yandex-team.ru/s-rogovskiy', '2022-01-20', NULL
);

INSERT INTO drills.drill_announces
DEFAULT VALUES;

INSERT INTO drills.drill_cards(
    "state", announce_id, business_unit, drill_type, datacenter, drill_date, time_interval, coordinator, anchorman, members, calendar_event, "comment", st_ticket, st_ticket_summary, st_ticket_description, updated_at, deleted_at
)
VALUES(
    'NEW', 3, 'eda', 'internal', 'MAN', '2032-05-17', '16:00 - 19:00', 'coord_eda', 'anchorman_eda', NULL, NULL, 'comment', NULL, NULL, NULL, '2022-01-11 00:00:00.000', NULL
);

INSERT INTO drills.drill_announces
DEFAULT VALUES;

INSERT INTO drills.drill_cards(
    "state", announce_id, business_unit, drill_type, datacenter, drill_date, time_interval, coordinator, anchorman, members, calendar_event, "comment", st_ticket, st_ticket_summary, st_ticket_description, updated_at, deleted_at
)
VALUES(
    'NEW', 4, 'lavka', 'internal', 'MAN', '2032-05-17', '10:00 - 21:00', 'coord_lavka', 'anchorman_lavka', NULL, NULL, 'comment', NULL, NULL, NULL, '2022-01-11 00:00:00.000', NULL
);

INSERT INTO drills.drill_announces
DEFAULT VALUES;

INSERT INTO drills.drill_cards(
    "state", announce_id, business_unit, drill_type, datacenter, drill_date, time_interval, coordinator, anchorman, members, calendar_event,comment, st_ticket, st_ticket_summary, st_ticket_description,updated_at,deleted_at
)
VALUES(
    'NEW', 5, 'taxi', 'internal', 'MAN', '2032-07-17', '16:00 - 19:00', 'temox', 'temox', 'test1', NULL,'comment',NULL,NULL,NULL,'2022-01-11',NULL
);
