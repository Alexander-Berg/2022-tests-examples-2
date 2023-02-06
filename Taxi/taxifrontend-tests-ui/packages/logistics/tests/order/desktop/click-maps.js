const orderPage = require('../../../pageobjects/order/order-page');
const {waitSomeValue} = require('../../../support/helpers');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Заполнение адреса кликом на карту', async function () {
        allureReporter.addTestId('taxiweb-1919');

        await orderPage.open('/order');
        await browser.$(orderPage.addressFrom).waitForExist({timeout: 30000});
        await expect(browser.$(orderPage.addressFrom)).toHaveValue('');
        await browser.$(orderPage.tagMaps).click();
        await waitSomeValue(orderPage.addressFrom, 5000, 'Поле Адрес отправителя осталось пустым');
        await browser.$(orderPage.tagMaps).click({x: 50, y: 30});
        await waitSomeValue(orderPage.addressTo, 5000, 'Поле Адрес получателя осталось пустым');
    });
});
