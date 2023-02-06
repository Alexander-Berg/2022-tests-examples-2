const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const timeToWaitElem = 50_000;
let statementNumber;

const checkRemoveModalWindow = () => {
    StatementPage.btnRemove.removeIcon.click();
    expect(StatementPage.btnRemove.modalWindow.window).toBeDisplayed();
    expect(StatementPage.btnRemove.modalWindow.btnYes).toBeDisplayed();
    expect(StatementPage.btnRemove.modalWindow.btnNo).toBeDisplayed();
};

describe('Удаление ведомости', () => {
    it('Preconditions: создать ведомость (при создании ведомость открывается автоматически)', () => {
        const testData = {
            keepMoney: '100',
            paymentMin: '1111',
            paymentMax: '',
        };

        ListStatementsPage.goTo();
        ListStatementsPage.addStatementButton.click();
        ListStatementsPage.fillAddStatementForm(testData);
        ListStatementsPage.addStatementForm.btnCreateDraft.click();
        StatementPage.waitingLoadThisPage(timeToWaitElem);

        statementNumber = StatementPage.getStatementNumber();
        expect(StatementPage.btnRemove.removeIcon).toBeDisplayed();
    });

    it('Нажать кнопку удаления ведомости', () => {
        checkRemoveModalWindow();
    });

    it('Нажать "Нет"', () => {
        StatementPage.btnRemove.modalWindow.btnNo.click();
        StatementPage.waitingLoadThisPage(timeToWaitElem);
        expect(StatementPage.statementHeaderStatus).toHaveText('Черновик');
    });

    it('Нажать кнопку удаления ведомости', () => {
        checkRemoveModalWindow();
    });

    it('Нажать "Да"', () => {
        StatementPage.btnRemove.modalWindow.btnYes.click();
        // тост об успешном удалении ведомости
        expect(StatementPage.btnRemove.tost).toBeDisplayed();

        // ведомость закрыта, отображается список ведомостей
        expect(ListStatementsPage.searchField).toBeDisplayed();

        // в списке ведомостей отсутствует удаленная ведомость
        ListStatementsPage.searchField.setValue(statementNumber);
        assert.isTrue(ListStatementsPage.reportTable.notFound.waitForDisplayed({timeout: 5000}));
    });
});
