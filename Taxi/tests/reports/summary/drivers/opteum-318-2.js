const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: время на линии',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Время на линии',
        td: 4,
        sortButtonIndex: 1,
        time: true,
    }),
);
