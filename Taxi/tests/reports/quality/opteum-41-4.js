const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

const LOW = '0';
const HIGH = '148';

describe('Сортировать водителей по Успешно завершенным заказам в таблице качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сортировать по возрастанию', () => {
        ReportsQuality.sortSuccessfullyCompletedOrders.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverSuccessfullyCompletedOrders.getText(), LOW);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverSuccessfullyCompletedOrders.getText(), HIGH);
    });

    it('Перейти на первую страницу', () => {
        ReportsQuality.firstPage.click();
    });

    it('Сортировать по убыванию', () => {
        ReportsQuality.sortSuccessfullyCompletedOrders.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverSuccessfullyCompletedOrders.getText(), HIGH);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverSuccessfullyCompletedOrders.getText(), LOW);
    });

});
