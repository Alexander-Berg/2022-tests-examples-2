const carSearchChecks = require('../../../../shared/reportsSummary/carSearchChecks');

describe(
    'Поиск по позывному в заданном периоде',

    () => carSearchChecks({
        path: '/cars'
            + '?date_from=2022-01-24'
            + '&date_to=2022-01-31',

        query: 'Тачила',
        plate: 'А123ААА',
    }),
);
