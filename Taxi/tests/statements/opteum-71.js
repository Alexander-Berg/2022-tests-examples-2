const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const timeToWaitElem = 30_000;
let statementNumber, statementRowNumber;

describe('Исполнение черновика ведомости', () => {
    it('Preconditions: создать ведомость (при создании ведомость открывается автоматически)', () => {
        const testData = {
            keepMoney: '100',
            paymentMin: '1',
            paymentMax: '',
        };

        ListStatementsPage.goTo();
        ListStatementsPage.addStatementButton.click();
        ListStatementsPage.fillAddStatementForm(testData);
        ListStatementsPage.addStatementForm.btnCreateDraft.click();
        StatementPage.waitingLoadThisPage(timeToWaitElem);
        statementNumber = StatementPage.getStatementNumber();
    });

    it('На странице черновика ведомости нажать кнопку "Выполнить"', () => {
        StatementPage.btnExecuting.waitForDisplayed({timeout: timeToWaitElem});
        StatementPage.btnExecuting.click();
        ListStatementsPage.statusDropdown.waitForDisplayed({timeout: timeToWaitElem});
        ListStatementsPage.statusDropdown.click();
        ListStatementsPage.statusDropdownItems.executing.click();

        if (!ListStatementsPage.reportTable.notFound.isDisplayed()) {
            $(`td*=${statementNumber}`).waitForDisplayed({
                timeout: timeToWaitElem,
            });

            statementRowNumber = ListStatementsPage.getRowNumberByStatementNumber(statementNumber);

            // у выполняемой ведомости изменился статус на "В работе"
            assert.equal(ListStatementsPage.getRowInTable(statementRowNumber).status.getText(), 'В работе');
            // тост о начале выполнения ведомости
            assert.isTrue(StatementPage.alert.isDisplayed());
        }
    });

    it('Дождаться окончания выполнения ведомости', () => {
        do {
            ListStatementsPage.statusDropdown.click();
            ListStatementsPage.statusDropdownItems.executed.click();
            ListStatementsPage.searchField.click();
            ListStatementsPage.clearWithBackspace(ListStatementsPage.searchField);
            ListStatementsPage.type(ListStatementsPage.searchField, statementNumber);

            try {
                $(`td*=${statementNumber}`).waitForDisplayed({
                    timeout: timeToWaitElem,
                });
            } catch {
                browser.refresh();
                continue;
            }

            break;
        // !FIXME: не использовать бесконечный цикл
        // eslint-disable-next-line no-constant-condition
        } while (true);

        // статус ведомости в списке "Обработана"
        assert.equal(ListStatementsPage.getRowInTable(statementRowNumber).status.getText(), 'Обработана');
    });

    it('Открыть обработанную ведомость', () => {
        statementRowNumber = ListStatementsPage.getRowNumberByStatementNumber(statementNumber);
        ListStatementsPage.getRowInTable(statementRowNumber).status.click();
        StatementPage.waitingLoadThisPage(timeToWaitElem);
        // в заголовке указан статус "Обработана"
        $('span*=Обработана').waitForDisplayed({timeout: timeToWaitElem});
        assert.equal(StatementPage.statementHeaderStatus.getText(), 'Обработана');

        // поля указания комиссии заблокированы на изменение
        assert.isTrue($$('span.Textinput_disabled')[0].isDisplayed());
        assert.isTrue($$('span.Textinput_disabled')[1].isDisplayed());
    });
});
