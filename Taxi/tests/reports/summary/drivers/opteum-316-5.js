const totalPriceChecks = require('../../../../shared/reportsSummary/totalPriceChecks');

describe(
    'Переход в отчет по транзакциям для каждой суммы: прочее',

    () => totalPriceChecks({
        path: '/drivers',
        td: 9,
        canBeOnlyZero: true,
        category: [
            'Прочие платежи партнера, заправки (комиссия)',
            'Прочие платежи платформы, заправки (кэшбэк)',
            'Прочие платежи платформы, заправки (чаевые)',
            'Прочие платежи платформы, заправки',
        ],
    }),
);
