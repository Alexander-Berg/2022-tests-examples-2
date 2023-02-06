const WorkRulesPage = require('../page/WorkRulesPage');
const {assert} = require('chai');

describe('Просмотр списка существующих условий ', () => {
    it('Открыть страницу условий работы', () => {
        WorkRulesPage.goTo();
    });

    it('Проверить заголовок страницы', () => {
        assert.equal(WorkRulesPage.title.getText(), 'Условия работы');
    });

    it('Проверить наличие списка существующих условий работы', () => {
        assert.isAtLeast(WorkRulesPage.allRows.length, 1);
    });
});
