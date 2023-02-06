const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 20_000;
const deltaMoney = 999;

let balance,
    driverName;

const addSpaces = (numberStr, dotIndex) => {
    if (numberStr.slice(0, dotIndex).length > 3) {
        const doublePart = numberStr.slice(dotIndex, numberStr.length);
        const intPart = [...numberStr.slice(0, dotIndex)].reverse().join('');

        const triplesParts = [];
        let triplesPartsCounter = 0;
        let onePart = '';

        for (let i = 0; i < intPart.length; i++) {
            onePart += intPart[i];

            if (onePart.length === 3) {
                triplesParts[triplesPartsCounter] = onePart;
                triplesPartsCounter++;
                onePart = '';
                continue;
            }

            if (i === intPart.length - 1) {
                triplesParts[triplesPartsCounter] = onePart;
            }
        }

        triplesParts.reverse();
        const result = triplesParts[triplesParts.length - 1].split('').reverse().join('');
        return result + doublePart;
    }

    return numberStr;
};

const balanceToText = number => {
    let str = String(number);
    let dotIndex = str.indexOf('.');

    if (dotIndex > 0) {
        str[dotIndex] = ',';
    } else {
        dotIndex = str.length;
        str = `${str},00`;
    }

    return addSpaces(str, dotIndex);
};

describe('Баланс: действие через Enter в карточке водителя', () => {
    it('Открыть карточку любого', () => {
        DriversPage.goTo();
        DriversPage.getRowInTable().fullName.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.getRowInTable().fullName.click();
    });

    it('Нажать на +/- в балансе водителя', () => {
        DriverCard.waitingLoadThisPage(timeToWaitElem);

        driverName = DriverCard.getDriverName().trim();
        balance = DriverCard.parseBalanceToFloat();

        DriverCard.balansUpButton.waitForDisplayed({timeout: timeToWaitElem});
        DriverCard.balansUpButton.click();

        DriverCard.paymentsSidemenu.moneyInput.waitForDisplayed({timeout: timeToWaitElem});
        browser.pause(1000);
        assert.equal(DriverCard.paymentsSidemenu.driverName.getText().trim(), driverName);
        assert.equal(DriverCard.paymentsSidemenu.transactionType.incoming.getProperty('checked'), true);
    });

    it('Указать любую сумму в поле "Сумма"', () => {
        browser.keys(`${deltaMoney}`);
    });

    it('Нажать на кнопку Enter', () => {
        browser.keys('Enter');
        DriverCard.paymentsSidemenu.driverName.waitForDisplayed({timeout: 5000, reverse: true});
        DriverCard.paymentsSidemenu.savedAlert.waitForDisplayed({timeout: 5000});
        browser.pause(5000);
        browser.refresh();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('Проверить, что баланс изменился на указанную сумму в истории баланса в карточке водителя', () => {
        const newBalance = DriverCard.parseBalanceToFloat();
        const newBalanceStr = $(`span*=${balanceToText(newBalance)}`);
        const balanceHistory = $('a*=История баланса');

        balanceHistory.click();
        newBalanceStr.waitForDisplayed({timeout: timeToWaitElem});
        assert.equal(newBalance, balance + deltaMoney);
    });

    it('Проверить, что баланс изменился на указанную сумму в отчёте о транзакциях ("приход/расход")', () => {
        const transactionsReport = 'https://fleet.tst.yandex.ru/reports/transactions/list?park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru';
        browser.url(transactionsReport);

        const driverNameSelector = $(`a*=${driverName}`);
        driverNameSelector.waitForDisplayed({timeout: timeToWaitElem});

        const deltaMoneySelector = $(`span*=${deltaMoney},00`);
        deltaMoneySelector.waitForDisplayed({timeout: timeToWaitElem});
    });
});
