const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Фильтрация по автомобилю', () => {
    let vehicle;

    it('Открыть страницу отчёт по заказам 350', () => {
        ReportsOrders.goTo();
    });

    it('Найти первый заполненный автомобиль', () => {
        for (let i = 1; i <= 15; i++) {
            const vehicleElem = ReportsOrders.getRow(i).vehicle;

            if (vehicleElem.isExisting()) {
                vehicle = vehicleElem.getText();
                return;
            }
        }

        throw new Error('Не найден заполненный автомобиль в списке');
    });

    it('В фильтр "Автомобиль" ввести код автомобиля из списка', () => {
        ReportsOrders.filtersList.vehicle.click();
        ReportsOrders.focusedInput.addValue(vehicle);
        browser.pause(1000);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('В списке отобразились заказы только с этим автомобилем', () => {
        ReportsOrders.allRows.vehicle.forEach(currentRowVehicle => {
            assert.equal(currentRowVehicle.getText(), vehicle);
        });
    });
});
