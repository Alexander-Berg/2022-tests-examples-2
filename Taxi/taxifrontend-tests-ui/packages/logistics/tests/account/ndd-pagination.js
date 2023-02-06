const nddPage = require('../../pageobjects/account/ndd');
const response = require('../../fixtures/ndd-claims.json');
const responsePagination = require('../../fixtures/ndd-claims-pagination.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница "Доставка в другой день" /account/ndd', () => {
    it('Пагинация списка заказов', async function () {
        allureReporter.addTestId('taxiweb-2129');

        const mockStations = await browser.mock(
            '**/api/b2b/platform/integration/v1/station/list?supply=true',
            {
                method: 'GET'
            }
        );
        const mockClaimsFirstPage = await browser.mock(
            '**/api/b2b/platform/integration/v1/claims/active?take_count=50&use_cursor=true',
            {
                method: 'GET'
            }
        );
        const mockClaimsSecondPage = await browser.mock(
            '**/api/b2b/platform/integration/v1/claims/active?take_count=50&use_cursor=true&cursor=*',
            {
                method: 'GET'
            }
        );

        mockStations.respond({has_more: false, stations: []}, {statusCode: 200});
        mockClaimsFirstPage.respond(response, {statusCode: 200});
        mockClaimsSecondPage.respond(responsePagination, {statusCode: 200});

        await nddPage.authorizeAndOpenNDD();

        // ожидание загрузки списка заявок, ждем появление id первой в списке
        await $('//*[text()="f2232330d"]').waitForDisplayed();
        const claims = await $$('//*[text()="Новая"]');
        await expect(claims.length).toEqual(50);

        // скролл до последней в списке заявки
        await claims[49].scrollIntoView();

        // ожидание загрузки списка заявок после скрола, ждем появление id первой заявки на второй странице
        await $('//*[text()="353536663"]').waitForDisplayed();
        await expect(await $$('//*[text()="Новая"]').length).toEqual(100);
    });
});
