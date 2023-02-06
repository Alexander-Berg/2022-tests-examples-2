const info = require('../../fixtures/shared-route/info-postcard.json');
const performerPosition = require('../../fixtures/shared-route/performer-position.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Шарилка', () => {
    it('Открытка в шарилке', async function () {
        allureReporter.addTestId('taxiweb-2032');

        const mockInfo = await browser.mock('**/4.0/cargo-c2c/v1/shared-route/info', {method: 'POST'});
        mockInfo.respond(info, {statusCode: 200});
        const mockPerformer = await browser.mock('**/4.0/cargo-c2c/v1/shared-route/performer-position', {method: 'POST'});
        mockPerformer.respond(performerPosition, {statusCode: 200});

        await browser.url('/route/f44265a0-dfb2-4236-bbc0-c72cfd0a1592');

        await expect(browser.$('//*[text()="Скачать Яндекс Go"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Чтобы тоже отправлять открытки"]')).toBeDisplayed();

        // Проверка для мобилки
        let windowSize = await browser.getWindowSize();
        if (windowSize.height < 801) {
            await browser.$('//button').click();
            await expect(browser.$('//*[text()="Создавайте свои открытки к посылкам в Яндекс Go"]')).toBeDisplayed();
        }
    });
});
