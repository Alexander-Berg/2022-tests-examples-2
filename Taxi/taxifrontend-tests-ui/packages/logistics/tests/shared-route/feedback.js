const info = require('../../fixtures/shared-route/info-finished.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Шарилка', () => {
    it('Шарилка. Оценка заказа пользователем', async function () {
        allureReporter.addTestId('taxiweb-2049');

        const mockInfo = await browser.mock('**/4.0/cargo-c2c/v1/shared-route/info', {method: 'POST'});
        mockInfo.respond(info, {statusCode: 200});
        const mockFeedback = await browser.mock('**/4.0/cargo-c2c/v1/shared-route/feedback', {method: 'POST'});
        mockFeedback.respond({"operation_id": "123"}, {statusCode: 200});

        await browser.url('/route/29245878-34d3-404a-a3ad-4e6a0f1d7b43');
        // Ждем загрузки страницы
        await browser.$('//*[text()="Доставлено"]').waitForDisplayed();

        // Проверка на мобилку, что бы открыть шторку
        let fiveStar = '//*[@id="root"]/div[1]/div[3]/div[1]/div[3]/div/div[1]/a[5]';
        let isMobile = await browser.$('//*[@id="root"]/div[2]/div/div[2]/div[1]').isExisting();
        if (isMobile) {
            fiveStar = '//*[@id="root"]/div[2]/div/div[2]/div[2]/div[1]/div[3]/div/div[1]/a[5]';
            await browser.$('//*[@id="root"]/div[2]/div/div[2]/div[1]').click();
            await browser.pause(1000);
        }

        // клик по пятой звезде
        await browser.$(fiveStar).click();
        await expect(mockFeedback).toBeRequestedWith({
            postData: expect.objectContaining({comment: "", reasons: [], score: 5})
        });

        // Клик по причине "Быстрее всех"
        await browser.$('//*[contains(text(),"Быстрее")]').click();
        await expect(mockFeedback).toBeRequestedWith({
            postData: expect.objectContaining({comment: "", reasons: [{"reason_id": "fast_delivery"}], score: 5})
        });

        const comment = 'Отзыв о доставке я написал'
        await browser.$('//*[text()="Отзыв о доставке"]').click()
        await browser.$('//input').setValue(comment)
        await browser.$('//button').click()

        await expect(mockFeedback).toBeRequestedWith({
            postData: expect.objectContaining({comment: comment, reasons: [{"reason_id": "fast_delivery"}], score: 5})
        });
    });
});
