const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 10_000;
let balance;
const deltaBalance = '100000';

describe('Карточка водителя: история баланса', () => {
    it('Перейти на страницу водителей', () => {
        DriversPage.goTo();
    });

    it('Перейти на страницу водителя', () => {
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('Открыть историю баланса в карточке водителя', () => {
        $('span=История баланса').click();
    });

    it('Запомнить состояние счета', () => {
        balance = Number.parseFloat(DriverCard.currentBalance.getText().replace(/\s+/g, ''));
    });

    it('Добавить / списать денег через кнопки + / -', () => {
        DriverCard.balansUpButton.click();
        browser.pause(200);
        browser.keys(deltaBalance);
        browser.pause(1000);
        browser.keys('Enter');
    });

    it('Обновить страницу', () => {
        let newBalance;

        browser.waitUntil(() => {
            browser.refresh();
            browser.pause(1000);

            DriverCard.currentBalance.waitForDisplayed({timeout: timeToWaitElem});
            newBalance = Number.parseFloat(DriverCard.currentBalance.getText().replace(/\s+/g, ''));
            return newBalance - balance === Number.parseInt(deltaBalance);
        });

        balance = newBalance;
    });

    it('Проверить изменение баланса в истории баланса', () => {
        const firstBalanceInTable = Number.parseFloat($('tbody tr:nth-child(1) td:nth-child(2) span').getText().replace(/\s+/g, ''));
        assert.isTrue(firstBalanceInTable === balance);
    });
});
