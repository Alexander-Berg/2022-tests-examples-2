INSERT INTO supportai.actions_miscs (id, project_id, misc_slug, misc_name)
VALUES
(1, 'detmir_dialog', 'transport_company_preproc', 'Обработка названий транспортных компаний'),
(2, 'detmir_dialog', 'transport_company_phone', 'Телефоны транспортных компаний'),
(3, 'detmir_dialog', 'transport_company_storage_time', 'Время хранения транспортных копаний')
;

INSERT INTO supportai.actions_miscs_container (id, misc_id, misc)
VALUES
(1, 1,
$$
{"5Post": ["5post"],
"ДПД": ["dpd"],
"Boxberry": ["boxberry"],
"TelePort": ["teleport"],
"Дали": ["дали"],
"СДЭК": ["сдэк"],
"PickPoint": ["pickpoint"],
"Стриж": ["стриж"],
"Логсис": ["логсис"],
"Курьерист": ["курьерист"],
"РЭД Экспресс": ["рэд экспресс"],
"Топ деливери": ["top-delivery"],
"Регион-Сервис": ["регион-сервис"],
"СберЛогистика": ["сберлогистика"]
}
$$
),
(2, 2,
$$
{"5Post": "+7(800)555-55-05",
"ДПД": "+7(910)440-44-34",
"Boxberry": "+7(800)222-80-00",
"TelePort": "+7(499)673-37-15(МСК) или +7(812)679-15-15(СПБ)",
"СДЭК": "+7(800)250-04-05",
"PickPoint": "+7(800)700-79-09",
"Далли": "+7(495)646-86-82",
"Стриж": "+7(495)660-54-24",
"Логсис": "+7(499)322-32-95",
"Курьерист": "+7(495)135-15-51",
"РЭД Экспресс": "+7(495)740-60-60",
"Топ деливери": "+7(495)660-36-83",
"Регион-Сервис": "+7(499)372-03-22",
"СберЛогистика": "+7(800)100-72-69"
}
$$
),
(3, 3,
$$
{"5Post": 3,
"Boxberry": 3,
"TelePort": 3,
"PickPoint": 7,
"СберЛогистика": 3
}
$$
);
