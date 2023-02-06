const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const timeToWaitElem = 10_000;

const testData = {
    instantPayouts: '10',
};

const defaultData = {
    instantPayouts: '1',
};

const driverName = 'opteum-299';

describe('выбор правила выплат', () => {
    it(`Открыть карточку своего тестового водителя ${driverName}`, () => {
        DriversPage.goTo();
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(2000);
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('изменить значение поля "Моментальные выплаты" в блоке "Моментальные выплаты"', () => {
        DetailsTab.fillInstantPayoutsBlock(testData.instantPayouts);
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
        DetailsTab.fillInstantPayoutsBlock(defaultData.instantPayouts);
        DriverCard.saveButton.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
        DetailsTab.checkAllChangeFields(defaultData);
    });
});
