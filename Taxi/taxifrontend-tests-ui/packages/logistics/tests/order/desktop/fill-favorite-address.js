const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;
const zoneinfo = require('../../../fixtures/zoneinfo.json');
const pinDropSuggest = require('../../../fixtures/suggest/suggest-pin-drop.json');
const zeroSuggest = require('../../../fixtures/suggest/suggest-zero-suggest.json');
const finalizeSuggest = require('../../../fixtures/suggest/suggest-finalize.json');

describe('Страница заказа /order', () => {
    it('Заполнение "избранного" адреса', async function () {
        allureReporter.addTestId('taxiweb-1593');

        const mockZoneinfo = await browser.mock('**/integration/turboapp/v1/zoneinfo');
        mockZoneinfo.respond(zoneinfo);
        const mock = await browser.mock('**/integration/turboapp/v1/suggest', {
            postData: (data) => typeof data === 'string'
        });
        mock.respond((request) => {
            let requestAction = JSON.parse(request.postData).action;
            if (requestAction === 'pin_drop') {
                return pinDropSuggest;
            }
            if (requestAction === 'zero_suggest') {
                return zeroSuggest;
            }
            if (requestAction === 'finalize') {
                return finalizeSuggest;
            }
        });
        await orderPage.open('/order/courier');

        await browser.$(orderPage.addressFrom).click();
        await browser.$(`//*[text()="Дом"]`).waitForClickable({timeout: 20000});
        await browser.$(`//*[text()="Дом"]`).click();

        await expect(browser.$(orderPage.addressFrom)).toHaveValue(finalizeSuggest.results[0].title.text);
        await expect(browser.$(orderPage.addressFromDoorphoneNumber)).toHaveValue(finalizeSuggest.results[0].doorphone_number);
        await expect(browser.$(orderPage.addressFromFloorNumber)).toHaveValue(finalizeSuggest.results[0].floor_number);
        await expect(browser.$(orderPage.addressFromPorchnumber)).toHaveValue(finalizeSuggest.results[0].porchnumber);
        await expect(browser.$(orderPage.addressFromQuartersNumber)).toHaveValue(finalizeSuggest.results[0].quarters_number);
    });
});
