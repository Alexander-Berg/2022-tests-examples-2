const info = require('../../fixtures/shared-route/info.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Шарилка', () => {
    it('Шарилка. Карточка заказа', async function () {
        allureReporter.addTestId('taxiweb-2048');

        const mockInfo = await browser.mock('**/4.0/cargo-c2c/v1/shared-route/info', {method: 'POST'});
        mockInfo.respond(info, {statusCode: 200});

        await browser.url('/route/f44265a0-dfb2-4236-bbc0-c72cfd0a1592');

        await expect(browser.$('//*[text()="Курьер будет у вас через ~121 мин"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Abibas1"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Александр"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Большой кузов"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="380 см в длину, 180 в ширину, 180 в высоту"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Зайцев Александр Трофимович"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="жёлтый Hyundai i40, В523УС777"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="+79999999998"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="проспект Красной Армии, 131"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="кв. 2, под. 2, этаж 2"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="комментарий так и так"]')).toBeDisplayed();

        // Проверка на мобилку, что бы открыть шторку
        let isMobile = await browser.$('//*[@id="root"]/div[2]/div/div[2]/div[1]').isExisting();
        if (isMobile) {
            await browser.$('//*[@id="root"]/div[2]/div/div[2]/div[1]').click();
            await browser.pause(1000);
        }

        await browser.$('//*[text()="Детали доставки"]').click();

        await expect(browser.$('//*[text()="Детали заказа"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Тариф Грузовой"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Большой кузов"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="380 см в длину, 180 в ширину, 180 в высоту"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="жёлтый Hyundai i40, номер В523УС777"]')).toBeDisplayed();
        await expect(browser.$('//*[text()="Индивидуальный предприниматель Юдаков Максим Викторович"]')).toBeDisplayed();
    });
});
