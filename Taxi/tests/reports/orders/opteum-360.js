const AutoCard = require('../../../page/AutoCard');
const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Переход в карточку автомобиля', () => {
    let licensePlateNumber;

    it('Открыть страницу отчёт по заказам', () => {
        ReportsOrders.goTo();
    });

    it('нажать на любой автомобиль в колонке "Автомобиль"', () => {
        licensePlateNumber = ReportsOrders.getRow().vehicle.getText();
        ReportsOrders.getRow().vehicleModel.click();
        browser.pause(2000);
        browser.switchWindow(licensePlateNumber);
        AutoCard.licensePlateNumber.waitForDisplayed();
    });

    it('Данные на странице отчётов и в карточке автомобиля совпадают', () => {
        assert.equal(AutoCard.licensePlateNumber.getValue(), licensePlateNumber);
    });
});
