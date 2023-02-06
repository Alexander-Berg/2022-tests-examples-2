const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница заказа /order', () => {
    it('Создание и отмена заказа, тариф Экспресс', async function () {
        allureReporter.addTestId('taxiweb-2119');

        await orderPage.authorizeAndOpen('/order/express');
        await orderPage.fillOrderFields();

        await orderPage.clickOrderBtn();
        await orderPage.cancelOrder();

        await browser.$(orderPage.cancelModalBtn).waitForDisplayed({reverse: true, timeout: 15000});
    });

    it('Создание и отмена заказа, тариф Курьер', async function () {
        allureReporter.addTestId('taxiweb-1597');

        await orderPage.authorizeAndOpen('/order/courier');
        await orderPage.fillOrderFields();

        await orderPage.clickOrderBtn();
        await orderPage.cancelOrder();

        await browser.$(orderPage.cancelModalBtn).waitForDisplayed({reverse: true, timeout: 15000});
    });

    it('Создание и отмена заказа, тариф Грузовой', async function () {
        allureReporter.addTestId('taxiweb-2120');

        await orderPage.authorizeAndOpen('/order/cargo');

        await browser.$(orderPage.addLoadersBtn).scrollIntoView();
        await browser.$(orderPage.addLoadersBtn).click();
        await browser.$(orderPage.addLoadersBtn).click();
        await browser.$('//*[text()="Маленький кузов"]/../..').click();

        await orderPage.fillOrderFields({
            addressFrom: 'москва садовническая 82с2',
            addressFromSuggest: 'Садовническая улица, 82с2',
            senderNumber: '9991233212',
            addressTo: 'москва льва толстого 16',
            addressToSuggest: 'улица Льва Толстого, 16'
        });

        await orderPage.clickOrderBtn();
        await orderPage.cancelOrder();

        await browser.$(orderPage.cancelModalBtn).waitForDisplayed({reverse: true, timeout: 15000});
    });
});
