const phoenixPage = require('../../pageobjects/phoenix/phoenix');
const {expectHaveSomeValue} = require('../../support/helpers');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Страница доставки сегодня /account2/cargo (phoenix)', () => {
    it('Повтор заказа', async function () {
        allureReporter.addTestId('taxiweb-1946');

        await phoenixPage.authorizeAndOpenCargo();
        // Повтор первой в списке заявки
        await browser.$('(//*[@title="Повторить"])[1]').click();

        await browser.waitUntil(
            async () => ((await browser.$(phoenixPage.addressFromInput).getValue()).length) >= 1,
            {
                timeout: 5000,
                timeoutMsg: 'Адрес "Откуда" не подгрузился в инпут с бэка'
            }
        );
        await expectHaveSomeValue(phoenixPage.addressFromInput);
        await expectHaveSomeValue(phoenixPage.addressToInput);
        await expectHaveSomeValue(phoenixPage.senderPhoneInput);
        await expectHaveSomeValue(phoenixPage.recipientNumberInput);
        await expectHaveSomeValue(phoenixPage.itemNameInput);
        await expectHaveSomeValue(phoenixPage.countItemInput);

        await browser.$(phoenixPage.createClaimFormBtn).click();

        await phoenixPage.waitUnlockClaimForm();
        await expect(browser.$(phoenixPage.acceptClaimFormBtn)).toBeDisplayed();

        let count = browser.$(phoenixPage.countItemInput).getValue();
        await browser.$(phoenixPage.countItemInput).setValue(count + 2);

        await expect(browser.$('//*[text()="Заявка изменена — нужна повторная оценка"]')).toBeDisplayed();
        await browser.$('//*[text()="Отправить на оценку"]').click();

        await phoenixPage.waitUnlockClaimForm();
        await browser.$(phoenixPage.acceptClaimFormBtn).click();

        await expect(browser.$(phoenixPage.cargoOrderForm)).not.toBeDisplayed();
    });
});
