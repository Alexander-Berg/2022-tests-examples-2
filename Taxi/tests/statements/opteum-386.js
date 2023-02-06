const ListStatementsPage = require('../../page/ListStatementsPage');
const {assert} = require('chai');

const defaultFormValues = {
    workTerms: 'Любые',
    status: 'Любой',
    keepMoney: '100',
    paymentMin: '1000',
    paymentMax: '5000',
    roundDownTo: 'Не округлять',
};

describe('Проверка содержимого формы создания ведомости', () => {
    it('открыть страницу ведомостей', () => {
        ListStatementsPage.goTo();
    });

    it('Справа от заголовка кликнуть кнопку "+"', () => {
        ListStatementsPage.addStatementButton.click();
        ListStatementsPage.addStatementForm.header.waitForDisplayed();
    });

    it('Проверить наличие элементов сайдменю', () => {
        assert.isTrue(ListStatementsPage.addStatementForm.header.isDisplayed());
        assert.isTrue(ListStatementsPage.addStatementForm.closeButton.isDisplayed());
        assert.equal(ListStatementsPage.addStatementForm.workTerms.getText(), defaultFormValues.workTerms);
        assert.equal(ListStatementsPage.addStatementForm.status.getText(), defaultFormValues.status);
        assert.equal(ListStatementsPage.addStatementForm.keepMoney.getValue(), defaultFormValues.keepMoney);
        assert.equal(ListStatementsPage.addStatementForm.paymentMin.getValue(), defaultFormValues.paymentMin);
        assert.equal(ListStatementsPage.addStatementForm.paymentMax.getValue(), defaultFormValues.paymentMax);
        assert.equal(ListStatementsPage.addStatementForm.roundDownTo.getText(), defaultFormValues.roundDownTo);
        assert.isTrue(ListStatementsPage.addStatementForm.checkBoxWithoutActiveOrder.isDisplayed());
        assert.isTrue(ListStatementsPage.addStatementForm.btnCreateDraft.isDisplayed());
    });
});
