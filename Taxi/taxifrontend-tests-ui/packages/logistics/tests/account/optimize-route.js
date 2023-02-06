const cargoPage = require('../../pageobjects/account/cargo');
const allureReporter = require('@wdio/allure-reporter').default;
const {fillAddress} = require('../../support/helpers');

describe('Страница доставки сегодня /account/cargo', () => {
    it('Оптимазация маршрута', async function () {
        allureReporter.addTestId('taxiweb-1010');

        await cargoPage.authorizeAndOpenCargo();
        await browser.$(cargoPage.createClaimBtn).click();
        await browser.$(cargoPage.cargoOrderForm).waitForDisplayed();

        await fillAddress(cargoPage.addressFromInput, 'Садовническая улица, 82с2');
        await fillAddress(cargoPage.addressToInput, 'улица Льва Толстого, 16');
        await browser.$(cargoPage.addAddressBtn).click();
        await fillAddress(cargoPage.addressTo2Input, 'Варшавское шоссе, 114А');
        await browser.$(cargoPage.addAddressBtn).click();
        await fillAddress(cargoPage.addressTo3Input, 'Мясницкая улица, 11');
        await browser.$(cargoPage.optimizeRouteBtn).click();

        await expect(browser.$('//*[text()="Текущий маршрут оптимизирован"]')).toBeDisplayed();
    });
});
