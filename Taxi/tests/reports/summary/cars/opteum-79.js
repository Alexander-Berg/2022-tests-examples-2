const carSearchChecks = require('../../../../shared/reportsSummary/carSearchChecks');

describe(
    'Поиск по СТС в заданном периоде',

    () => carSearchChecks({
        path: '/cars'
            + '?date_from=2022-01-24'
            + '&date_to=2022-01-31',

        query: 7_878_787_878,
        plate: 'А007АВ25',
    }),
);
