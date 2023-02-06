const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

let uniqueDriverNumber;

describe('Создать водителя', () => {
    it('Открыть список водителей', () => {
        DriversPage.goTo();
    });

    it('нажать кнопку добавления водителя', () => {
        DriversPage.addDriverButton.waitForDisplayed({timeout: 6000});
        DriversPage.addDriverButton.click();
    });

    it('заполнить карточку водителя', () => {
        uniqueDriverNumber = DriverCard.fillRequiredFields();
    });

    it('открыть список водителей, сортированный по дате создания', () => {
        browser.pause(5000);
        DriversPage.goTo();
        browser.pause(5000);
    });

    it('среди водителей присутствует новый водитель', () => {
        let isDataDisplayed = false;
        const arr = $$('[class*=Table_driver_license]');

        arr.forEach(el => {
            if (el.getText() === uniqueDriverNumber) {
                isDataDisplayed = true;
            }
        });

        assert.isTrue(isDataDisplayed);
    });
});
