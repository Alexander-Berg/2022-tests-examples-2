const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

describe('Фильтрация по условиям работы', () => {
    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('В фильтре "Условия работы" указать "4Q"', () => {
        ReportsQuality.selectWorkRuleByValue('4Q');
        assert.equal(ReportsQuality.resultTable.firstWorkRule.getText(), '4Q');
    });

    it('В фильтре "Условия работы" указать "Yandex"', () => {
        ReportsQuality.selectWorkRuleByValue('Yandex');
        assert.equal(ReportsQuality.resultTable.firstWorkRule.getText(), 'Yandex');
    });

    it('Полностью очистить поле "Условия работы", кликнув по "Х"', () => {
        ReportsQuality.filtersBlock.workRules.clear.click();
        assert.equal(ReportsQuality.resultTable.firstWorkRule.getText(), 'empty');
    });

});
