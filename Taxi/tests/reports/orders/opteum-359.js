const DriverCard = require('../../../page/driverCard/DriverCard');
const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Переход в карточку водителя', () => {
    let driverName, vehicle;

    it('Открыть страницу отчёт по заказам', () => {
        ReportsOrders.goTo();
    });

    it('нажать на ФИО любого водителя в колонке "Водитель"', () => {
        vehicle = ReportsOrders.getRow().vehicle.getText();
        driverName = ReportsOrders.getRow().driver.getText();

        ReportsOrders.getRow().driver.click();
        DriverCard.switchTab();

        DriverCard.lastName.waitForDisplayed();
    });

    it('Данные на странице отчётов и в карточке водителя совпадают', () => {
        expect(DriverCard.vehicleLink).toHaveTextIncludes(vehicle);
        assert.isTrue(driverName.includes(DriverCard.lastName.getText()));
        assert.isTrue(driverName.includes(DriverCard.firstName.getText()));
    });
});
