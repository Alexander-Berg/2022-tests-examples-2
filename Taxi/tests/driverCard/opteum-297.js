const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const timeToWaitElem = 10_000;

const testData = {
    details: {
        status: 'Работает',
    },
};

const defaultData = {
    details: {
        status: 'Не работает',
    },
};

const driverName = 'opteum-297';

describe('смена статуса профиля', () => {
    it(`Открыть карточку своего тестового водителя ${driverName}`, () => {
        DriversPage.goTo();
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(2000);
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('изменить значение поля "Статус" в блоке "Детали"', () => {
        DetailsTab.fillDetailsBlock(testData.details);
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
        DetailsTab.fillDetailsBlock(defaultData.details);
        DriverCard.saveButton.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
        DetailsTab.checkAllChangeFields(defaultData);
    });
});
