const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Скрытие/отображение столбцов в таблице', () => {

    it('Открыть страницу отчёт по заказам', () => {
        ReportsOrders.goTo();
    });

    it('нажать на кнопку редактирования колонок таблицы', () => {
        ReportsOrders.editColumnButton.click();
    });

    it('поочередно скрыть все колонки таблицы', () => {
        let columnCount = ReportsOrders.allColumns.length;

        ReportsOrders.columnsEditSVG.forEach(element => {

            if (element.getCSSProperty('opacity').value === 0) {
                return;
            }

            element.click();
            columnCount--;
            assert.equal(columnCount, ReportsOrders.allColumns.length);
        });
    });

    it('поочередно отобразить все колонки таблицы', () => {
        let columnCount = ReportsOrders.allColumns.length;

        ReportsOrders.columnsEditButtons.forEach((element, i) => {

            if (i === 0) {
                columnCount++;
                return;
            }

            element.click();
            assert.equal(columnCount, ReportsOrders.allColumns.length);
            columnCount++;
        });
    });
});
