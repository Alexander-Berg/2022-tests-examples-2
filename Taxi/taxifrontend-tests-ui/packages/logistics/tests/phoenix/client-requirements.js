const phoenixPage = require('../../pageobjects/phoenix/phoenix');
const allureReporter = require('@wdio/allure-reporter').default;
let mock;

describe('Страница доставки сегодня /account2/cargo (phoenix)', () => {
    beforeEach(async function () {
        await phoenixPage.authorizeAndOpenCargo();
        mock = await browser.mock('**/api/b2b/phoenix/cargo-claims/v2/claims/create**', {
            method: 'POST'
        });
        await phoenixPage.fillClaimForm();
    });

    it('Проверка спецтребований. Простановка требования, тариф Курьер', async function () {
        allureReporter.addTestId('taxiweb-1982');

        await browser.$(phoenixPage.selectCourierTariffBtn).click();
        await browser.$('//*[text()="Только курьер на машине"]/..').click();

        // достаем id заявки для последующего поиска этой заявки в списке
        let claimId;
        mock.respond(req => {
            claimId = req.body.id;
            return req.body;
        });

        await browser.$(phoenixPage.createClaimFormBtn).click();
        await expect(mock).toBeRequestedWith({
            postData: expect.objectContaining({
                client_requirements: {
                    cargo_options: ['auto_courier'],
                    taxi_class: 'courier'
                }
            })
        });

        await phoenixPage.waitUnlockClaimForm();
        await browser.$(phoenixPage.acceptClaimFormBtn).click();

        await expect(browser.$(phoenixPage.cargoOrderForm)).not.toBeDisplayed();
        await browser.$(`//*[@href="#claim/add/${claimId}"]/../..`).click();
        await expect(browser.$('//*[text()="Курьер на машине"]')).toBeDisplayed();
    });

    it('Проверка спецтребований. Отмена требования, тариф Экспресс', async function () {
        allureReporter.addTestId('taxiweb-1982');

        await browser.$(phoenixPage.selectExpressTariffBtn).click();
        await browser.$('//*[text()="От двери до двери"]/..').click();

        // достаем id заявки для последующего поиска этой заявки в списке
        let claimId;
        mock.respond(req => {
            claimId = req.body.id;
            return req.body;
        });

        await browser.$(phoenixPage.createClaimFormBtn).click();
        await expect(mock).toBeRequestedWith({
            postData: expect.objectContaining({
                client_requirements: {
                    door_to_door: false,
                    taxi_class: 'express'
                }
            })
        });

        await phoenixPage.waitUnlockClaimForm();
        await browser.$(phoenixPage.acceptClaimFormBtn).click();

        await expect(browser.$(phoenixPage.cargoOrderForm)).not.toBeDisplayed();
        await browser.$(`//*[@href="#claim/add/${claimId}"]/../..`).click();
        await expect(browser.$('//*[text()="От двери до двери"]')).not.toBeDisplayed();
    });
});
