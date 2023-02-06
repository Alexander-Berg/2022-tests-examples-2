const phoenixPage = require('../../pageobjects/phoenix/phoenix');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account2/cargo (phoenix)', () => {
    it('Создание заявки БЕЗ карты оплаты в профиле', async function () {
        allureReporter.addTestId('taxiweb-2121');

        await phoenixPage.authorizeAndOpenCargo('phoenix-autotest-card');
        await phoenixPage.fillClaimForm();
        await browser.$(phoenixPage.selectExpressTariffBtn).click();

        const mock = await browser.mock('**/api/b2b/phoenix/cargo-claims/v2/claims/create*', {
            method: 'POST'
        });

        await browser.$(phoenixPage.createClaimFormBtn).click();
        let claimId;
        mock.respond(req => {
            claimId = req.body.id;
            return req.body;
        });

        await expect(
            browser.$('//*[text()="Нет доступных способов оплаты. Обратитесь к администратору."]')
        ).toBeDisplayed();
        await browser.$(phoenixPage.closeFormBth).click();
        await expect(browser.$(phoenixPage.cargoOrderForm)).not.toBeDisplayed();
        await browser.$(`//*[@href="#claim/add/${claimId}"]/../..`).click();
        await expect(
            browser.$('//*[text()="Нет доступных способов оплаты. Обратитесь к администратору."]')
        ).toBeDisplayed();
    });
});
