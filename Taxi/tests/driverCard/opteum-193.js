const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const convertCurrencyToNumber = text => Number(text.replace(/[^\d.-]+/g, ''));

describe('Смоук: увеличить и уменьшить баланс', () => {

    it('Открыть профиль водителя из списка', () => {
        DriversPage.goTo();
        $('tbody [class*=Table_name] a').waitForDisplayed({timeout: 5000});
        $('tbody [class*=Table_name] a').click();
    });

    let deltaBalance, startBalance;

    it('запомнить состояние счета', () => {
        startBalance = convertCurrencyToNumber(DriverCard.currentBalance.getText());
    });

    const delta = 1000;

    it('увеличить баланс', () => {
        $('[class*=Balance_buttons]').waitForDisplayed();
        DriverCard.balansUpButton.click();
        $('[placeholder="Сумма"]').addValue(delta);
        browser.pause(500);
        browser.keys('Enter');
        $('.Alert').waitForDisplayed();
    });

    it('баланс увеличился', () => {
        browser.waitUntil(() => {
            browser.refresh();
            DriverCard.currentBalance.waitForDisplayed();
            deltaBalance = convertCurrencyToNumber(DriverCard.currentBalance.getText());
            return deltaBalance === startBalance + delta;
        });
    });

    it('уменьшить баланс', () => {
        $('[class*=Balance_buttons]').waitForDisplayed();
        DriverCard.balansDownButton.click();
        $('[placeholder="Сумма"]').addValue(delta);
        browser.pause(500);
        browser.keys('Enter');
        $('.Alert').waitForDisplayed();
    });

    it('баланс вернулся к первоначальному', () => {
        browser.waitUntil(() => {
            browser.refresh();
            const currBalance = convertCurrencyToNumber(DriverCard.currentBalance.getText());

            return startBalance === currBalance;
        });

    });
});
