const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const timeToWaitElem = 10_000;

const testData = {
    workRules: {
        limit: '10',
    },
};

const defaultData = {
    workRules: {
        limit: '0',
    },
};

const driverName = 'opteum-302';

describe('настройка лимита по счёту', () => {
    it(`Открыть карточку своего тестового водителя ${driverName}`, () => {
        DriversPage.goTo();
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(2000);
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('изменить значение поля "Лимит по счёту" в блоке "Условия работы" на другое случайное валидное значение', () => {
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
