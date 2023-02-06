const orderPage = require('../../../pageobjects/order/order-page');
const zoneinfo = require('../../../fixtures/zoneinfo-cargo-express.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Недоступность тарифа в зоне', async function () {
        allureReporter.addTestId('taxiweb-1732');

        const mock = await browser.mock('**/integration/turboapp/v1/zoneinfo');
        mock.respond(zoneinfo);
        await orderPage.open('/order');

        await expect(browser.$('//*[text()="Грузовой"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Доставка"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Курьер"]')).not.toBeDisplayed();
    });
});
