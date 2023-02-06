const totalPriceChecks = require('../../../../shared/reportsSummary/totalPriceChecks');

describe(
    'Переход в отчет по транзакциям для каждой суммы: комиссия парка',

    () => totalPriceChecks({
        path: '/drivers',
        td: 8,
        category: [
            'Комиссия партнера за бонус',
            'Комиссия партнера за заказ',
            'Комиссия партнера за перевод',
            'Комиссия партнера за смену',
        ],
    }),
);
