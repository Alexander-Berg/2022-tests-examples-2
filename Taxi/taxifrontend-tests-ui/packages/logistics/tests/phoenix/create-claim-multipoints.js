const phoenixPage = require('../../pageobjects/phoenix/phoenix');
const {fillAddress} = require('../../support/helpers');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account2/cargo (phoenix)', () => {
    it('Создание заявки с мультиточками', async function () {
        allureReporter.addTestId('taxiweb-1949');

        await phoenixPage.authorizeAndOpenCargo();
        await phoenixPage.fillClaimForm();

        await browser.$(phoenixPage.addAddressBtn).click();
        await fillAddress(phoenixPage.addressTo2Input,
            'улица Ватутина, 14', 'новосибирск ватутина 14');
        await browser.$(phoenixPage.recipient2NameInput).setValue('Дед');
        await browser.$(phoenixPage.recipient2NumberInput).setValue('+79991236789');
        await browser.$(phoenixPage.createClaimFormBtn).click();

        // Проверка получения нотификации что для точки нет отправлений
        await expect(browser.$('.Notification__error-with-button').isExisting);

        await browser.$(phoenixPage.addItemBtn).click();

        await browser.$(phoenixPage.item2NameInput).setValue('коробка вторая');
        await browser.$(phoenixPage.countItem2Input).setValue('1');
        await browser.$(phoenixPage.address2Selector).click();
        await browser.$(phoenixPage.address2SelectorInput).setValue('Ватутина');
        await browser.$('.Select-menu-outer').click();

        await browser.$(phoenixPage.selectExpressTariffBtn).click();
        await browser.$(phoenixPage.createClaimFormBtn).click();

        await phoenixPage.waitUnlockClaimForm();
        await expect(browser.$(phoenixPage.acceptClaimFormBtn)).toBeClickable();
    });
});
