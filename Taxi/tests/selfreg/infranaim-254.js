const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');

describe('Наличие элементов страницы /vehicle-type', () => {
    it('пройти до страницы /vehicle-type', () => {
        vehiclePage.open();
    });

    it('Элементы отображаются при открытии страницы', () => {
        vehiclePage.checkScreenshot('selfreg-vehicle-type');
    });
});
