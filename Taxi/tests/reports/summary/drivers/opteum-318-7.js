const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: прочее',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Прочее',
        td: 9,
        sortButtonIndex: 6,
    }),
);
