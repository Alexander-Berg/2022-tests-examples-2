const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

const LOW = '4,20';
const HIGH = '5,00';

describe('Сортировать водителей по Рейтингу на конец периода в таблице качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сортировать водителей по возрастанию', () => {
        ReportsQuality.sortEndPeriodRateColumn.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverEndPeriodRate.getText(), LOW);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverEndPeriodRate.getText(), HIGH);
    });

    it('Перейти на первую страницу', () => {
        ReportsQuality.firstPage.click();
    });

    it('Сортировать водителей по убыванию', () => {
        ReportsQuality.sortEndPeriodRateColumn.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverEndPeriodRate.getText(), HIGH);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverEndPeriodRate.getText(), LOW);
    });

});
