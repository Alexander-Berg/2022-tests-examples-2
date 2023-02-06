const phoenixPage = require('../../pageobjects/phoenix/phoenix');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account2/cargo (phoenix)', () => {
    it('Создание заявки и подтверждение', async function () {
        allureReporter.addTestId('taxiweb-1948');

        await phoenixPage.authorizeAndOpenCargo();
        await phoenixPage.fillClaimForm();
        await browser.$(phoenixPage.selectExpressTariffBtn).click();
        await browser.$(phoenixPage.createClaimFormBtn).click();

        await phoenixPage.waitUnlockClaimForm();
        const mock = await browser.mock('**/api/b2b/phoenix/cargo-claims/v1/claims/accept*', {
            method: 'POST'
        });

        let claimId;
        mock.respond(req => {
            claimId = req.body.id;
            return req.body;
        });

        await browser.$(phoenixPage.acceptClaimFormBtn).click();
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
        await expect(browser.$(phoenixPage.cargoOrderForm)).not.toBeDisplayed();
    });
});
