const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');

describe('Выбор значения "На автомобиле" /vehicle-type', () => {
    it('пройти до страницы /vehicle-type', () => {
        vehiclePage.open();
    });

    it('выбрать тип Автомобиль', () => {
        vehiclePage.selectCourierType('vehicle');
    });
});
