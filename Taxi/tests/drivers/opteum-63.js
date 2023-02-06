const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

const timeToWaitElem = 5000;

const testData = {
    driverLicense: '4587757576',
};

describe('Поиск истории водителя по ВУ', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('Установить фильтр состояния "На линии"', () => {
        DriversPage.goTo();
        DriversPage.statusesDropdown.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.statusesDropdown.click();
        DriversPage.selectDropdownItem('На линии');
        browser.keys('Escape');
        browser.pause(2000);
    });

    it('Перейти в карточку любого водителя', () => {
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage();
    });

    it('В карточке водителя под полем ВУ нажать "Проверить водителя"', () => {
        DriverCard.checkDriver.btnCheckDriver.waitForDisplayed({timeout: timeToWaitElem});
        const linkToHistoryPage = DriverCard.checkDriver.btnCheckDriver.getAttribute('href');
        DriverCard.checkDriver.btnCheckDriver.click();
        browser.pause(1000);
        browser.switchWindow(linkToHistoryPage);
        DriverCard.checkDriver.historyWindow.header.waitForDisplayed({timeout: timeToWaitElem});
    });

    it(`В поле поиска ввести ВУ ${testData.driverLicense}`, () => {
        DriverCard.clearWithBackspace(DriverCard.checkDriver.historyWindow.inputDriverLicense);
        DriverCard.type(DriverCard.checkDriver.historyWindow.inputDriverLicense, testData.driverLicense);
        browser.keys('Enter');
        browser.pause(2000);
        DriverCard.checkDriver.historyWindow.avatarBlock.waitForDisplayed({timeout: timeToWaitElem});
    });
});
