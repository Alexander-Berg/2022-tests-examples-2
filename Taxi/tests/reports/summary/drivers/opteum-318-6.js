const tableSortChecks = require('../../../../shared/reportsSummary/tableSortChecks');

describe(
    'Сортировка данных в столбцах: комиссии парка',

    () => tableSortChecks({
        path: '/drivers',
        name: 'Комиссии парка',
        td: 8,
        sortButtonIndex: 5,
    }),
);
