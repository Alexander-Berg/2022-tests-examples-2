const {uncheckColumnChecks} = require('../../../shared/reportsTransactions');

describe(
    'Отчет по транзакциям. Проверка добавления столбцов. Список.',

    () => uncheckColumnChecks({
        path: '/list'
            + '?from=20211220'
            + '&to=20211220',
        columns: [
            'Дата',
            'Водитель',
            'Категория',
            'Сумма',
            'Документ',
            'Инициатор',
            'Комментарий',
        ],
        uncheckIndex: 2,
    }),
);
