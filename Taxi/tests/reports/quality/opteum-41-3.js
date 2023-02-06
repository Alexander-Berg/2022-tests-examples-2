const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

const LOW = '1';
const HIGH = '170';

describe('Сортировать водителей по Предложенным заказам в таблице качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сортировать водителей по возрастанию', () => {
        ReportsQuality.sortRequestedOrders.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverRequestedOrders.getText(), LOW);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverRequestedOrders.getText(), HIGH);
    });

    it('Перейти на первую страницу', () => {
        ReportsQuality.firstPage.click();
    });

    it('Сортировать водителей по убыванию', () => {
        ReportsQuality.sortRequestedOrders.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverRequestedOrders.getText(), HIGH);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverRequestedOrders.getText(), LOW);
    });
});
