const totalPriceChecks = require('../../../../shared/reportsSummary/totalPriceChecks');

describe(
    'Переход в отчет по транзакциям для каждой суммы: наличные',

    () => totalPriceChecks({
        path: '/parks',
        td: 9,
        category: [
            'Наличные',
            'Наличные, поездка партнера',
        ],
    }),
);
