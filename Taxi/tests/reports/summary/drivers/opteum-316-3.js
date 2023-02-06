const totalPriceChecks = require('../../../../shared/reportsSummary/totalPriceChecks');

describe(
    'Переход в отчет по транзакциям для каждой суммы: комиссия платформы',

    () => totalPriceChecks({
        path: '/drivers',
        td: 7,
        category: [
            'Комиссия платформы за бонус',
            'Комиссия платформы за заказ',
            'Комиссия платформы за режимы «По делам» и «Мой район»',
            'Комиссия платформы, НДС',
            'Смена, НДС',
            'Смена',
        ],
    }),
);
