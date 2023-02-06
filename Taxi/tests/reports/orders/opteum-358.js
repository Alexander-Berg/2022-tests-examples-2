const ReportsOrders = require('../../../page/ReportsOrders');
const ReportsOrdersModeration = require('../../../page/ReportsOrdersModeration');
const {assert} = require('chai');

describe('Переход в раздел модерации заказов', () => {

    it('Открыть страницу отчёт по заказам', () => {
        ReportsOrders.goTo();
    });

    it('нажать на ссылку "Модерация заказов"', () => {
        ReportsOrders.ordersModeration.click();
        ReportsOrdersModeration.title.waitForDisplayed();
        assert.isTrue(ReportsOrdersModeration.title.isExisting());
    });
});
