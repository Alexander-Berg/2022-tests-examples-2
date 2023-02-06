const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: безналичные платежи',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Безналичные платежи',
        td: 6,
        sortButtonIndex: 3,
    }),
);
