const OrderPage = require('../../../page/OrderPage');
const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Переход в карточку заказа', () => {

    it('Открыть страницу отчёт по заказам 357', () => {
        ReportsOrders.goTo();
    });

    it('нажать на код первого заказа в колонке "Код заказа"', () => {
        const orderCode = ReportsOrders.allRows.orderCode[0].getText();
        const pageName = `Заказ ${orderCode}`;
        ReportsOrders.allRows.orderCode[0].click();
        browser.pause(1000);

        try {
            browser.switchWindow(pageName);
        } catch {
            browser.pause(10_000);
            browser.switchWindow(pageName);
        }

        OrderPage.orderHeader.waitForDisplayed({timeout: 10_000});
        assert.equal(pageName, OrderPage.orderHeader.getText());
    });
});
