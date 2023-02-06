const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: наличные',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Наличные',
        td: 5,
        sortButtonIndex: 2,
    }),
);
