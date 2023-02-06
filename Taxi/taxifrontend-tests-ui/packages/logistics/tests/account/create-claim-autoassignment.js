const cargoPage = require('../../pageobjects/account/cargo');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account/cargo', () => {
    it('Создание заявки c автоподбором', async function () {
        allureReporter.addTestId('taxiweb-966');

        await cargoPage.authorizeAndOpenCargo();
        await cargoPage.fillClaimForm();
        await browser.$(cargoPage.autoAssignmentCheckbox).click();
        await expect(browser.$(cargoPage.selectExpressTariffBtn)).not.toBeDisplayed();

        await browser.$(cargoPage.widthInput).setValue('1');
        await browser.$(cargoPage.heightInput).setValue('1');
        await browser.$(cargoPage.lengthInput).setValue('1');
        await browser.$(cargoPage.weightInput).setValue('5');

        await browser.$(cargoPage.createClaimFormBtn).scrollIntoView();
        await browser.$(cargoPage.createClaimFormBtn).click();

        // Автоматически выбран тариф грузовой
        await expect(
            browser.$('//*[text()="Грузовой"]/../..//*[text()="Выбрано"]')
        ).toBeDisplayed();
    });
});
