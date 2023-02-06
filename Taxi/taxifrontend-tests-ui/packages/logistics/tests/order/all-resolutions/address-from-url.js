const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Передача адреса из url', async function () {
        allureReporter.addTestId('taxiweb-2038');

        await orderPage.open('/order/cargo?from=60.576400,56.800772&to=60.588346,56.833390');
        await expect(browser.$(orderPage.addressFrom)).toHaveValue('улица Академика Бардина, 46');
        await expect(browser.$(orderPage.addressTo)).toHaveValue('улица Сакко и Ванцетти, 58');
    });
});
