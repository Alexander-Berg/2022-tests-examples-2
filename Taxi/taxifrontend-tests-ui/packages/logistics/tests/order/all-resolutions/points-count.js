const orderPage = require('../../../pageobjects/order/order-page');
const zoneinfo = require('../../../fixtures/zoneinfo.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Ограничение количества точек', async function () {
        allureReporter.addTestId('taxiweb-1641');

        const mock = await browser.mock('**/integration/turboapp/v1/zoneinfo');
        mock.respond(zoneinfo);
        await orderPage.mockSuggestToMoscow();
        await orderPage.open('/order/cargo')

        await orderPage.clickAddAddressBtnTimes(5);
        await expect(browser.$(orderPage.addAddressBtn)).not.toBeClickable();

        await browser.$(orderPage.expressTariffBtn).click();
        await expect(browser.$(orderPage.addAddressBtn)).toBeClickable();

        await browser.$(orderPage.courierTariffBtn).click();
        await expect(browser.$(orderPage.addAddressBtn)).not.toBeClickable();
    });
});
