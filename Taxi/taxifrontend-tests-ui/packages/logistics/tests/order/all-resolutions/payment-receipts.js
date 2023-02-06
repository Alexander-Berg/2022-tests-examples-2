const orderPage = require('../../../pageobjects/order/order-page');
const list = require('../../../fixtures/list.json');
const itemPayCash = require('../../../fixtures/item-pay-cash.json');
const itemPayCard = require('../../../fixtures/item-pay-card.json');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Чеки в истории заказов', async function () {
        allureReporter.addTestId('taxiweb-1918');
        const mock = await browser.mock('**/4.0/orderhistory/v2/list');
        mock.respond(list);
        // мок для search, что бы не отображались активные заказы
        const mockSearch = await browser.mock('**/integration/turboapp/v1/orders/search');
        mockSearch.respond({"orders": []}, {statusCode: 200});

        const mockItem = await browser.mock('**/4.0/orderhistory/v2/item');
        mockItem.respond(itemPayCash, {statusCode: 200});

        // Чек при оплате наличными
        await orderPage.authorizeAndOpen('/order');
        await browser.$(orderPage.myOrdersTab).click();
        await browser.$('(//*[text()="Чек"]/..)[2]').click();
        await expect(browser.$('//*[text()="Оплата наличными"]')).toBeDisplayed();

        // Чек при 500 ручки item
        await mockItem.restore();
        mockItem.respond({}, {statusCode: 500});
        await browser.$('(//*[text()="Чек"]/..)[2]').click();
        await expect(browser.$('//*[text()="Чек не найден. Повторите позже"]')).toBeDisplayed();

        // Чек при оплате картой
        await mockItem.restore();
        mockItem.respond(itemPayCard, {statusCode: 200});
        await browser.$('(//*[text()="Чек"]/..)[1]').click();

        // Почему то в гриде вебдрайвер делает проверку toHaveUrlContaining на первой вкладке
        // ждем открытия второй (getWindowHandles вернет два хендлера) и переключаемся руками
        let handles = await orderPage.waitTabOpen(15000)
        await browser.switchToWindow(handles[1]);

        // проверяется открытие новой вкладки с урлом, который пришел в ручке item
        // урл траста в ответе заменен, что бы тест не валился из-за траста
        await expect(browser).toHaveUrlContaining(itemPayCard.order.receipt.url_with_embedded_pdf,
            {wait: 15000});
    });
});
