const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

const LOW = '-0,27';
const HIGH = '+0,15';

describe('Сортировать водителей по Изменению рейтинга за период в таблице качество', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Сортировать водителей по возрастанию', () => {
        ReportsQuality.sortRatePeriodChangesColumn.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverRatePeriodChanges.getText(), LOW);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverRatePeriodChanges.getText(), HIGH);
    });

    it('Перейти на первую страницу', () => {
        ReportsQuality.firstPage.click();
    });

    it('Сортировать водителей по убыванию', () => {
        ReportsQuality.sortRatePeriodChangesColumn.click();
    });

    it('Проверить первое значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.firstDriverRatePeriodChanges.getText(), HIGH);
    });

    it('Перейти на последнюю страницу', () => {
        ReportsQuality.lastPage.click();
    });

    it('Проверить последнее значение после сортировки', () => {
        assert.equal(ReportsQuality.resultTable.lastDriverRatePeriodChanges.getText(), LOW);
    });

});
