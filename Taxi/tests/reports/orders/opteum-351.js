const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Фильтрация по коду заказа', () => {
    let orderCode;

    it('Открыть страницу отчёт по заказам 351', () => {
        ReportsOrders.goTo();
    });

    it('В фильтр "Код заказа" ввести код заказа из списка', () => {
        orderCode = ReportsOrders.getRow(2).orderCode.getText();
        ReportsOrders.filtersList.orderCode.click();
        ReportsOrders.filtersList.orderCode.setValue(orderCode);
        browser.pause(1000);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('В списке отобразились заказы только с этим кодом', () => {
        ReportsOrders.allRows.orderCode.forEach(currentRowOrderCode => {
            assert.equal(currentRowOrderCode.getText(), orderCode);
        });
    });
});
