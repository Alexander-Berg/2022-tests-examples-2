const dict = require('../../../pagesDict');
const vehiclePage = new dict.vehiclePage();

describe('Выбор значения "На автомобиле" /vehicle-type', () => {
    it('пройти до страницы /vehicle-type', () => {
        vehiclePage.open();
    });

    it('выбрать тип Автомобиль', () => {
        vehiclePage.selectCourierType('vehicle');
    });
});
