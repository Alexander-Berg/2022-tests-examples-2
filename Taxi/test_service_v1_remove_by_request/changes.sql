/* 'park_id': 'extra_super_park_id' */
INSERT INTO changes_0 (
    park_id,
    id,
    date,
    object_id,
    object_type,
    user_id,
    user_name,
    counts,
    values,
    ip
)
VALUES
(
    'extra_super_park_id_0',
    'extra_super_entry_id_0',
    '2010-10-10 10:10:10',
    'extra_super_object_id_0',
    'TaxiServer.Models.Driver.Driver',
    'extra_super_user_id_0',
    'Акакий Вениаминович',
    1,
    '{"DateCreate":{"current":"03.01.2010 13:50:28","old":"27.12.2009 20:39:26"}}',
    '2a02:2168:1ec3:'
), (
    'extra_super_park_id_0',
    'extra_super_entry_id_1',
    '2010-10-11 10:10:11',
    'extra_super_object_id_0',
    'TaxiServer.Models.Driver.Driver',
    NULL,
    NULL,
    2,
    '{"DateCreate":{"current":"01.01.0001 0:00:00","old":"23.12.2015 7:15:58"},' ||
     '"Смена ТС":{"current":"[75] FORD GALAXIE","old":"[80] FORD GALAXY"}}',
    '109.188.125.30'
), (
    'extra_super_park_id_0',
    'extra_super_entry_id_2',
    '2010-10-12 10:10:12',
    'extra_super_object_id_0',
    'Entities.Driver.DriverWorkRule',
    'extra_super_user_id_1',
    'Тамара Боромировна',
    1,
    '{"Лимит":{"current":"-600,00","old":"50,00"}}',
    NULL
), (
    'extra_super_park_id_0',
    'extra_super_entry_id_4',
    '2010-10-12 10:10:12',
    'extra_super_object_id_0',
    'Entities.Driver.DriverWorkRule',
    '',
    'Изольда Рудольфовна',
    1,
    '{"Смена ТС":{"current":"[88] FORD GALAXY","old":"[83] FORD GALAXY"}}',
    '109.188.125.30'
);
