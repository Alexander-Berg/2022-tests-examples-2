const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

const LOW = '0';
const HIGH = '47';

describe('Сортировать водителей по Отлично выполненным заказам в таблице качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сортировать по возрастанию', () => {
        ReportsQuality.sortPerfectlyDoneOrders.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverPerfectlyDoneOrders.getText(), LOW);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverPerfectlyDoneOrders.getText(), HIGH);
    });

    it('Перейти на первую страницу', () => {
        ReportsQuality.firstPage.click();
    });

    it('Сортировать по убыванию', () => {
        ReportsQuality.sortPerfectlyDoneOrders.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverPerfectlyDoneOrders.getText(), HIGH);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverPerfectlyDoneOrders.getText(), LOW);
    });
});
