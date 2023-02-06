const phoenixPage = require('../../pageobjects/phoenix/phoenix');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account2/cargo (phoenix)', () => {
    before(async () => {
        await phoenixPage.authorizeAndOpenCargo();
    });

    it('Фильтрация заявок по ID', async function () {
        allureReporter.addTestId('taxiweb-1945');

        await browser
            .$(phoenixPage.filterClaimIdInput)
            .setValue('73c3e8619704491f829f24d532bfb0c2');
        await browser.pause(1000);
        await browser
            .$('[href="#claim/add/73c3e8619704491f829f24d532bfb0c2"]')
            .waitForDisplayed({timeout: 25000});
        await expect(await browser.$$('//*[@title="Повторить"]').length).toEqual(1);
    });

    it('Фильтрация заявок по телефону', async function () {
        allureReporter.addTestId('taxiweb-1945');

        await browser.url('/account2/cargo');
        await browser.$(phoenixPage.filterClaimIdInput).setValue('+79123458990');
        await browser
            .$('[href="#claim/add/13a24a17aa884633b366ef7774e38b46"]')
            .waitForDisplayed({timeout: 25000});
        await expect(await browser.$$('//*[@title="Повторить"]').length).toEqual(2);
    });

    it('Фильтрация заявок по дате', async function () {
        allureReporter.addTestId('taxiweb-1945');

        await browser.url('/account2/cargo');
        await browser.$(phoenixPage.filterFromInput).setValue('01.04.2022');
        await browser.$(phoenixPage.filterToInput).setValue('02.04.2022');
        await browser
            .$('[href="#claim/add/d31b24a3414941509a42c8a45c8698c8"]')
            .waitForDisplayed({timeout: 25000});
        await expect(await browser.$$('//*[@title="Повторить"]').length).toEqual(6);
    });

    it('Фильтрация заявок по ID и дате', async function () {
        allureReporter.addTestId('taxiweb-1945');

        await browser.url('/account2/cargo');
        await browser
            .$(phoenixPage.filterClaimIdInput)
            .setValue('2ea2f323e0e44cdfbd53ef548d4944c9');
        await browser.$(phoenixPage.filterFromInput).setValue('25.04.2022');
        await browser.$(phoenixPage.filterToInput).setValue('26.04.2022');
        await browser
            .$('[href="#claim/add/2ea2f323e0e44cdfbd53ef548d4944c9"]')
            .waitForDisplayed({timeout: 25000});
        await expect(await browser.$$('//*[@title="Повторить"]').length).toEqual(1);
    });

    it('Фильтрация заявок. Подстановка фильтров из url', async function () {
        allureReporter.addTestId('taxiweb-1945');

        await browser.url(
            '/account2/cargo?searchBy=claim_id&dateFrom=2022-04-01T00%3A00%3A00%2B03%3A00&dateTo=2022-04-02T00%3A00%3A00%2B03%3A00&s=d31b24a3414941509a42c8a45c8698c8'
        );
        await expect(
            browser.$('[href="#claim/add/d31b24a3414941509a42c8a45c8698c8"]')
        ).toBeDisplayed();
        await expect(await browser.$$('//*[@title="Повторить"]').length).toEqual(1);
    });
});
