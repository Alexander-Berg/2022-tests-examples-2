const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const timeToWaitElem = 15_000;
let infoFromRow;

describe('Просмотр ведомости', () => {
    it('Открыть страницу ведомостей', () => {
        ListStatementsPage.goTo();
        ListStatementsPage.statusDropdown.click();
        ListStatementsPage.statusDropdownItems.executed.click();
        ListStatementsPage.getRowInTable(1).status.waitForDisplayed({timeout: timeToWaitElem});
    });

    it('Выбрать любую ведомость в списке, запомнить значения полей', () => {
        infoFromRow = ListStatementsPage.mapSelectorsToText(ListStatementsPage.getRowInTable(1));
    });

    it('Открыть страницу выбранной ведомости', () => {
        ListStatementsPage.getRowInTable(1).status.click();
        StatementPage.waitingLoadThisPage(timeToWaitElem);
    });

    it('Сравнить значения на странице ведомости со значениями данной ведомости из списка ведомостей', () => {
        assert.equal(StatementPage.getStatementNumber(), infoFromRow.number.replace(/[^\d+]/g, ''));
        assert.equal(StatementPage.statementHeaderStatus.getText(), infoFromRow.status);

        if (StatementPage.total.getText().includes(',')) {
            assert.equal(
                StatementPage.total
                    .getText().slice(0, Math.max(0, StatementPage.total.getText().indexOf(',')))
                    .replace(/[^\d+]/g, ''),
                infoFromRow.payoutsTotal.slice(0, Math.max(0, infoFromRow.payoutsTotal.indexOf(','))).replace(/[^\d+]/g, ''),
            );
        } else {
            assert.equal(StatementPage.total.getText().replace(/[^\d+]/g, ''), infoFromRow.payoutsTotal.slice(0, Math.max(0, infoFromRow.payoutsTotal.indexOf(','))).replace(/[^\d+]/g, ''));
        }

        if (Number.parseInt(infoFromRow.numberOfDrivers) > 0) {
            assert.equal(
                StatementPage
                    .getColumn(1)[0]
                    .getText()
                    .replace(/[^\d+]/g, ''),
                infoFromRow.numberOfDrivers.replace(/[^\d+]/g, ''),
            );
        } else {
            assert.isTrue(ListStatementsPage.reportTable.notFound.isDisplayed());
        }
    });
});
