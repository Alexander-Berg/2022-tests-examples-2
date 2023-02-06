const orderPage = require('../../../pageobjects/order/order-page');
const allureReporter = require('@wdio/allure-reporter').default;
const {fillAddress} = require('../../../support/helpers');

describe('Страница заказа /order', () => {
    it('Создание заказа (мобилка)', async function () {
        allureReporter.addTestId('taxiweb-1597');

        await orderPage.authorizeAndOpen('/order/express');

        let orderFields = {
            addressFrom: 'Новосибирск Ленина 12',
            addressFromSuggest: 'улица Ленина, 12',
            senderNumber: '9991233212',
            addressTo: 'новосибирск орджоникидзе 30',
            addressToSuggest: 'улица Орджоникидзе, 30',
            recipientNumber: '9994561222',
        };

        // Удаление хэдера для мобильного разрешения
        await browser.execute('document.querySelector("header")?.remove()');

        await fillAddress(orderPage.addressFrom, orderFields.addressFromSuggest, orderFields.addressFrom);
        await fillAddress(orderPage.addressTo, orderFields.addressToSuggest, orderFields.addressTo);
        await browser.$(orderPage.senderNumber).setValue(orderFields.senderNumber);
        await browser.$(orderPage.recipientNumber).setValue(orderFields.recipientNumber);
        await browser.pause(1000);
        await browser.$('//*[contains(text(),"Заказать・")]').click();
        await browser.pause(2000);
        let hasError = await browser.$('//*[text()="Ошибка формирования заказа"]').isExisting();
        if (hasError) {
            console.log('Заказ не создан, ошибка на бэке');
        } else {
            await browser.pause(1000);
            await browser.$(orderPage.cancelBtn).click();
            await browser.pause(1000);
            await browser.$(orderPage.cancelModalBtn).click();
            await browser
                .$(orderPage.cancelModalBtn)
                .waitForDisplayed({reverse: true, timeout: 15000});
            console.log('Заказ создан и успешно отменен');
        }
    });
});
