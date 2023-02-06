const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

describe('Фильтр по водителю в разделе Качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('В фильтре "Водитель" ввести имя "Сид" и выбрать первого водителя из списка совпадений', () => {
        ReportsQuality.selectDriverByValue('Сид');
        assert.equal(ReportsQuality.resultTable.firstDriver.getText(), 'Баррет Сид');
    });

    it('Ввести номер телефона "+70006543811" и выбрать найденного водителя', () => {
        ReportsQuality.selectDriverByValue('+70006543811');
        ReportsQuality.resultTable.secondDriver.waitForDisplayed();
        assert.equal(ReportsQuality.resultTable.secondDriver.getText(), 'Белотицкий Вадим');
    });

    it('Удалить водителя Сид из поля поиска, кликнув на "Х" возле имени', () => {
        ReportsQuality.filtersBlock.clearFirstDriver.click();
        ReportsQuality.resultTable.firstDriver.waitForDisplayed();
        assert.equal(ReportsQuality.resultTable.firstDriver.getText(), 'Белотицкий Вадим');
    });

    it('Ввести позывной "C326CC37" и выбрать найденного водителя', () => {
        ReportsQuality.selectDriverByValue('C326CC37');
        ReportsQuality.resultTable.firstDriver.waitForDisplayed();
        assert.equal(ReportsQuality.resultTable.firstDriver.getText(), 'Вэн Юн Тя');
    });

    it('Полностью очистить поле поиска "Водитель", кликнув по "Х" в самом конце строки', () => {
        ReportsQuality.filtersBlock.clearAllDrivers.click();
        assert.equal(ReportsQuality.driversCount.getText(), 'Количество водителей: 210');
    });

});
