const cargoPage = require('../../pageobjects/account/cargo');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account/cargo', () => {
    it('Редактирование заявки', async function () {
        allureReporter.addTestId('taxiweb-1006');

        await cargoPage.authorizeAndOpenCargo();
        await cargoPage.fillClaimForm();
        await browser.$(cargoPage.selectExpressTariffBtn).click();
        await browser.$(cargoPage.createClaimFormBtn).scrollIntoView();
        await browser.$(cargoPage.createClaimFormBtn).click();
        // ожидание разблокировки полей и кнопки формы, считаем что после этого заявка рассчитана
        await browser.$('.amber-button_disabled').waitForExist({reverse: true, timeout: 30000});
        await browser.pause(1000);
        await browser.$(cargoPage.closeFormBth).click();

        await expect(browser.$(cargoPage.cargoOrderForm)).not.toBeDisplayed();

        await browser.$(cargoPage.editBtn).click();

        await expect(browser.$(cargoPage.cargoOrderForm)).toBeDisplayed();
        await expect(browser.$(cargoPage.itemNameInput)).toHaveValue('Коробка нормальная');
    });
});
