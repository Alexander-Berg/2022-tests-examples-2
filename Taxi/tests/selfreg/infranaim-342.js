const { assert } = require('chai');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');

describe('Выбор значения "На велосипеде" /vehicle-type', () => {
    it('пройти до страницы /vehicle-type', () => {
        vehiclePage.open();
    });

    it('Выбор значения "На велосипеде" /vehicle-type', () => {
        vehiclePage.selectCourierType('cycle');
        assert.equal(vehiclePage.btnRdActive.getText(), 'На велосипеде');
    });
});
