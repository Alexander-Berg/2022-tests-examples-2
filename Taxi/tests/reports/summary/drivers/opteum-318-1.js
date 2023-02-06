const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: успешно завершённые заказы',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Успешно завершённые заказы',
        td: 3,
        sortButtonIndex: 0,
    }),
);
