const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: комиссия платформы',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Комиссия платформы',
        td: 7,
        sortButtonIndex: 4,
    }),
);
