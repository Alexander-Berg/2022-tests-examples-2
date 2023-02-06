const carSearchChecks = require('../../../../shared/reportsSummary/carSearchChecks');

describe(
    'Поиск по номеру авто в заданном периоде: найдено',

    () => carSearchChecks({
        path: '/cars'
            + '?date_from=2022-01-24'
            + '&date_to=2022-01-31',

        query: 'А007АВ25',
    }),
);
