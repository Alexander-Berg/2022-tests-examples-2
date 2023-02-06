const totalPriceChecks = require('../../../../shared/reportsSummary/totalPriceChecks');

describe(
    'Переход в отчет по транзакциям для каждой суммы: наличные',

    () => totalPriceChecks({
        path: '/drivers',
        td: 5,
        category: [
            'Наличные',
            'Наличные, поездка партнера',
        ],
    }),
);
