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
    /* full row */
    /* author is dispatcher*/
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
    /* row without 'user_id' and 'user_name' */
    /* author is platform */
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
    /* row without 'ip' */
    /* author is dispatcher*/
    'extra_super_park_id_0',
    'extra_super_entry_id_2',
    '2010-10-12 10:10:12',
    'extra_super_object_id_0',
    'TaxiServer.Models.Driver.Driver',
    'extra_super_user_id_1',
    'Тамара Боромировна',
    1,
    '{"Лимит":{"current":"-600,00","old":"50,00"}}',
    NULL
), (
    /* row without 'object_type' */
    /* author is dispatcher */
    'extra_super_park_id_0',
    'extra_super_entry_id_3',
    '2020-02-22 22:22:22',
    'extra_super_object_id_1',
    NULL,
    'extra_super_user_id_1',
    'Тамара Боромировна',
    1,
    '{"CommisisonForSubventionPercent":{"current":"6","old":"0"}}',
    '109.188.125.30'
), (
    /* row with empty 'user_id' */
    /* author is platform */
    'extra_super_park_id_0',
    'extra_super_entry_id_4',
    '2010-10-12 10:10:12',
    'extra_super_object_id_0',
    'MongoDB.Docs.Driver.DriverDoc',
    '',
    'Изольда Рудольфовна',
    1,
    '{"Смена ТС":{"current":"[88] FORD GALAXY","old":"[83] FORD GALAXY"}}',
    '109.188.125.30'
), (
    /* author is dispatcher */
    'extra_super_park_id_0',
    'extra_super_entry_id_5',
    '2020-02-23 22:22:23',
    'extra_super_object_id_1',
    'Entities.Driver.DriverWorkRule',
    'extra_super_user_id_1',
    'Тамара Боромировна',
    1,
    '{"WorkshiftCommissionPercent":{"current":"22,00","old":"22"}}',
    '109.188.125.30'
), (
    /* row without 'ip' */
    /* author is dispatcher */
    'extra_super_park_id_0',
    'extra_super_entry_id_6',
    '2020-02-24 22:22:24',
    'extra_super_object_id_1',
    'Entities.Driver.DriverWorkRule',
    'extra_super_user_id_7',
    'Техподдержка',
    1,
    '{"DisableDynamicYandexCommission":{"current":"False","old":"True"}}',
    NULL
), (
    /* row with empty 'ip' */
    /* author is dispatcher */
    'extra_super_park_id_0',
    'extra_super_entry_id_7',
    '2020-02-25 22:22:24',
    'extra_super_object_id_1',
    'Entities.Driver.DriverWorkRule',
    'extra_super_user_id_7',
    'Техподдержка',
    1,
    '{"DisableDynamicYandexCommission":{"current":"False","old":"True"}}',
    ''
), (
    /* author is dispatcher */
    'extra_super_park_id_1',
    'extra_super_entry_id_0',
    '2010-10-13 10:10:13',
    'extra_super_object_id_0',
    'MongoDB.Docs.Car.CarDoc',
    'extra_super_user_id_2',
    'Гаврила Визимирович',
    1,
    '{"Service":{"current":"None","old":"None"}}',
    '2a02:6b8:0:3711::1:12'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_1',
    '2011-11-11 11:11:11',
    'extra_super_object_id_1',
    'TaxiServer.Models.Driver.Driver',
    NULL,
    'Support technique',
    2,
    '{"DateCreate":{"current":"22.03.2016 2:53:30","old":"31.01.2016 13:35:44"},' ||
     '"WorkStatus":{"current":"Уволен","old":"Работает"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_2',
    '2012-02-02 02:02:02.000000',
    'extra_super_object_id_2',
    'MongoDB.Docs.Car.CarDoc',
    '',
    'TechSupport hire API (new)',
    1,
    '{"Number":{"current":"О986МР56","old":"О986МР55"}}',
    '::ffff:176.14.2'
), (
    /* row without 'user_id' and 'user_name' */
    /* author is platform */
    'extra_super_park_id_1',
    'extra_super_entry_id_3',
    '2013-03-01 03:03:01.000000',
    'extra_super_object_id_3',
    'Entities.Driver.DriverWorkRule',
    NULL,
    NULL,
    2,
    '{"YandexDisablePayUserCancelOrder":{"old":"","current":"False"},' ||
     '"WorkshiftsEnabled":{"old":"","current":"True"}}',
    '::ffff:176.14.2'
)
, (
    /* author is driver*/
    'extra_super_park_id_1',
    'extra_super_entry_id_4',
    '2012-02-03 02:02:03.000000',
    'extra_super_object_id_2',
    'MongoDB.Docs.Car.CarDoc',
    'extra_super_user_id_5',
    'driver',
    2,
    '{"Id":{"current":"5dc5216101123b786a285e62","old":""},' ||
     '"CarId":{"current":"f645b7c9d5e5216104574e521610f731","old":""}}',
    '::ffff:176.14.2'
), (
    /* author is driver*/
    'extra_super_park_id_1',
    'extra_super_entry_id_5',
    '2012-02-04 02:02:04.000000',
    'extra_super_object_id_2',
    'MongoDB.Docs.Car.CarDoc',
    'extra_super_user_id_5',
    'Driver',
    1,
    '{"Id":{"current":"5dc5216101123b786a285e62","old":""}}',
    '::ffff:176.14.2'
), (
    /* author is fleet-api*/
    'extra_super_park_id_1',
    'extra_super_entry_id_6',
    '2014-04-04 04:04:04.000000',
    'extra_super_object_id_4',
    'MongoDB.Docs.Car.CarDoc',
    'tralala',
    'API7 Key tralala',
    1,
    '{"Number":{"current":"О986МР57","old":"О986МР56"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_7',
    '2011-11-12 11:11:12',
    'extra_super_object_id_1',
    'TaxiServer.Models.Driver.Driver',
    NULL,
    'Tech support',
    1,
    '{"DateCreate":{"current":"22.03.2016 2:53:30","old":"31.01.2016 13:35:44"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_8',
    '2011-11-13 11:11:13',
    'extra_super_object_id_1',
    'TaxiServer.Models.Driver.Driver',
    NULL,
    'TechSupport API',
    1,
    '{"DateCreate":{"current":"22.03.2016 2:53:30","old":"31.01.2016 13:35:44"}}',
    '::ffff:176.14.2'
), (
    /* row without 'user_name' */
    /* author is platform*/
    'extra_super_park_id_1',
    'extra_super_entry_id_9',
    '2013-03-02 03:03:02.000000',
    'extra_super_object_id_3',
    'Entities.Driver.DriverWorkRule',
    'extra_super_user_id_6',
    NULL,
    1,
    '{"IsEnabled":{"old":"","current":"False"}}',
    '::ffff:176.14.2'
), (
    /* row without 'user_id' */
    /* author is platform*/
    'extra_super_park_id_1',
    'extra_super_entry_id_10',
    '2013-03-03 03:03:03.000000',
    'extra_super_object_id_3',
    'Entities.Driver.DriverWorkRule',
    NULL,
    'lipisin',
    1,
    '{"IsDriverFixEnabled":{"old":"","current":"False"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_11',
    '2011-11-14 11:11:14',
    'extra_super_object_id_1',
    'Yandex.Taximeter.Core.Repositori',
    '',
    'TechSupport hire API (new)',
    1,
    '{"Смена ТС":{"current":"Skoda Rapid [391]","old":"Пусто"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_12',
    '2011-11-15 11:11:15',
    'extra_super_object_id_1',
    'Yandex.Taximeter.Core.Repositori',
    '',
    'Techninė pagalba',
    1,
    '{"Смена ТС":{"current":"Skoda Rapid [391]","old":"Пусто"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_13',
    '2011-11-16 11:11:16',
    'extra_super_object_id_1',
    'Yandex.Taximeter.Core.Repositori',
    '',
    'Техподдержка',
    1,
    '{"Смена ТС":{"current":"Skoda Rapid [391]","old":"Пусто"}}',
    '::ffff:176.14.2'
), (
    /* author is tech-support*/
    'extra_super_park_id_1',
    'extra_super_entry_id_14',
    '2011-11-16 11:11:17',
    'extra_super_object_id_1',
    'Yandex.Taximeter.Core.Repositori',
    NULL,
    'Техподдержка',
    1,
    '{"Смена ТС":{"current":"Skoda Rapid [391]","old":"Пусто"}}',
    '::ffff:176.14.2'
), (
    /* row with 'user_name'='platform' */
    /* author is platform*/
    'extra_super_park_id_1',
    'extra_super_entry_id_15',
    '2013-03-04 03:03:04.000000',
    'extra_super_object_id_3',
    'Entities.Driver.DriverWorkRule',
    '',
    'platform',
    1,
    '{"IsEnabled":{"old":"False","current":"True"}}',
    '::ffff:176.14.2'
)
, (
    /* row with 'user_name'='Платформа' */
    /* author is platform*/
    'extra_super_park_id_1',
    'extra_super_entry_id_16',
    '2013-03-04 03:03:04.000000',
    'extra_super_object_id_3',
    'Entities.Driver.DriverWorkRule',
    NULL,
    'Платформа',
    1,
    '{"IsDriverFixEnabled":{"old":"","current":"False"}}',
    NULL
), (
    /* row with empty 'user_id' */
    /* author is platform*/
    'extra_super_park_id_0',
    'extra_super_entry_id_17',
    '2010-10-12 10:10:12',
    'extra_super_object_id_0',
    'TaxiServer.Models.Driver.Driver',
    NULL,
    'driver',
    1,
    '{"Comment":{"current":"списал  7000","old":"вернется позже"}}',
    '2a02:2168:1ec3:'
), (
    /* row with empty 'user_id' */
    /* author is platform*/
    'extra_super_park_id_0',
    'extra_super_entry_id_18',
    '2010-10-15 10:10:15',
    'extra_super_object_id_0',
    'TaxiServer.Models.Driver.Driver',
    NULL,
    'API7 Key tralala',
    1,
    '{"ProviderSelected":{"current":"Свои, Яндекс","old":"Свои, Яндекс, UpUp"}}',
    '2a02:2168:1ec3:'
)
