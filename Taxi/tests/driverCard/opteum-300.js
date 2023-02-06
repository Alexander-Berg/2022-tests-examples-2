const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const timeToWaitElem = 10_000;

const testData = {
    workRules: {
        workRules: '11111',
        limit: '10',
        dateStart: '15.10.2021',
        checkBoxPlatformOrders: false,
        checkBoxPartnerOrders: true,
        checkBoxCashlessRides: true,
    },
};

const defaultData = {
    workRules: {
        workRules: '1111',
        limit: '0',
        dateStart: '16.10.2021',
        checkBoxPlatformOrders: true,
        checkBoxPartnerOrders: false,
        checkBoxCashlessRides: false,
    },
};

const driverName = 'opteum-300';

describe('выбор условия работы', () => {
    it(`Открыть карточку своего тестового водителя ${driverName}`, () => {
        DriversPage.goTo();
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(2000);
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('изменить значения всех изменяемых полей и чекбоксов в блоке "Условия работы" на случайные данные', () => {
        DetailsTab.fillWorkRulesBlock(testData.workRules);
    });

    it('нажать на кнопку "Сохранить"', () => {
        DriverCard.saveButton.click();
    });

    it('обновить страницу', () => {
        browser.refresh();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
        DetailsTab.checkAllChangeFields(testData);
    });

    it(`Вернуть дефолтные данные водителя ${driverName}`, () => {
        DetailsTab.fillWorkRulesBlock(defaultData.workRules);
        DriverCard.saveButton.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
        DetailsTab.checkAllChangeFields(defaultData);
    });
});
