const cargoPage = require('../../pageobjects/account/cargo');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account/cargo', () => {
    it('Создание заявки и подтверждение', async function () {
        allureReporter.addTestId('taxiweb-967');

        await cargoPage.authorizeAndOpenCargo();
        await cargoPage.fillClaimForm();
        await browser.$(cargoPage.selectExpressTariffBtn).click();
        await browser.$(cargoPage.createClaimFormBtn).scrollIntoView();
        await browser.$(cargoPage.createClaimFormBtn).click();

        // ожидание разблокировки полей и кнопки формы, считаем что после этого заявка рассчитана
        await browser.$('.amber-button_disabled').waitForExist({reverse: true, timeout: 30000});
        await browser.pause(1000);
        const mock = await browser.mock('**/api/b2b/cargo-claims/v1/claims/accept*', {
            method: 'POST'
        });

        let claimId;
        mock.respond(req => {
            claimId = req.body.id;
            return req.body;
        });

        await browser.$(cargoPage.acceptClaimFormBtn).click();
        await expect(mock).toBeRequestedWith({
            response: {
                id: expect.stringMatching('.*'),
                skip_client_notify: false,
                user_request_revision: '1',
                status: 'accepted',
                version: 1
            }
        });
        await browser.$(`//*[@href="#claim/add/${claimId}"]/../..`).click();
        await expect(browser.$(`//span[text()='${claimId}']`)).toBeDisplayed();
        await expect(browser.$(cargoPage.cargoOrderForm)).not.toBeDisplayed();
    });
});
