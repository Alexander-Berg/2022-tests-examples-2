const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

const LOW = '0';
const HIGH = '7';

describe('Сортировать водителей по Заказам с оценкой 3 или ниже в таблице качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сортировать по возрастанию', () => {
        ReportsQuality.sortOrdersRated3OrLess.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverOrdersRated3OrLess.getText(), LOW);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverOrdersRated3OrLess.getText(), HIGH);
    });

    it('Перейти на первую страницу', () => {
        ReportsQuality.firstPage.click();
    });

    it('Сортировать по убыванию', () => {
        ReportsQuality.sortOrdersRated3OrLess.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverOrdersRated3OrLess.getText(), HIGH);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverOrdersRated3OrLess.getText(), LOW);
    });

});
