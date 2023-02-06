const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');

const testData = [
    {
        timeToWaitStatement: 60_000,
        workTerm: '4Q',
        status: 'Не работает',
        keepMoney: '50',
        paymentMin: '111',
        paymentMax: '555',
        roundDownTo: '100',
    },
];

describe('Создание новой ведомости', () => {
    it('Справа от заголовка кликнуть кнопку "+"', () => {
        ListStatementsPage.goTo();
        ListStatementsPage.addStatementButton.click();
    });

    it('Создать ведомость', () => {
        for (let i = 0; i < testData.length; i++) {
            ListStatementsPage.fillAddStatementForm(testData[i]);
            ListStatementsPage.addStatementForm.btnCreateDraft.click();

            if (StatementPage.waitingLoadThisPage(5000)) {
                StatementPage.checkingRowsByTestData(testData[i]);
            }

            StatementPage.btnExecuting.waitForDisplayed({timeout: testData[i].timeToWaitStatement});

            if (i !== testData.length - 1) {
                StatementPage.btnArrowBack.click();
                browser.refresh();
                ListStatementsPage.addStatementButton.waitForDisplayed({timeout: 5000});
                ListStatementsPage.addStatementButton.click();
            }
        }
    });
});
