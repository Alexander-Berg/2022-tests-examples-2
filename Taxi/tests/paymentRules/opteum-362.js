const PaymentRules = require('../../page/transferRequests/PaymentRules');

const columnList = [
    'Колонки таблицы',
    'название',
    'комиссия парка, %',
    'Мин. комиссия,  ₽',
    'мин. сумма',
    'макс. сумма',
    'Макс. сумма вывода в день, ₽',
    'Минимальный баланс',
    'дата создания',
    'дата изменения',
];

describe('Скрытие столбцов в таблице', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('нажать на кнопку редактирования колонок таблицы', () => {
        PaymentRules.btnEditTable.click();
    });

    it('отобразился список колонок таблицы', () => {
        expect(PaymentRules.tableColumnsList).toHaveTextEqual(columnList);
    });

    it('колонку "Название" нельзя скрыть', () => {
        const disabledColumnsCounter = 2;
        expect(PaymentRules.tableColumnsListDisabledItems).toHaveElemLengthEqual(disabledColumnsCounter);
    });

    it('поочередно скрыть все колонки таблицы', () => {
        for (let i = 2; i < PaymentRules.tableColumnsList.length; i++) {
            if (PaymentRules.tableColumnsListCheckboxes[i].isDisplayed()) {
                PaymentRules.tableColumnsList[i].click();
            }
        }
    });

    it('все колонки таблицы, кроме колонки "Название", скрыты', () => {
        const visibleColumnsCounter = 2;
        expect(PaymentRules.tableHeaders).toHaveElemLengthEqual(visibleColumnsCounter);
    });
});
