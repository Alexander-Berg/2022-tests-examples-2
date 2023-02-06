const ListStatementsPage = require('../../page/ListStatementsPage');
const StatementPage = require('../../page/StatementPage');
const {assert} = require('chai');

const testData = {
    status: ListStatementsPage.statuses.executed,
    statementNumber: '39',
};

describe('Выгрузка ведомости в файл: нельзя скачать выполненную ведомость с > 1000 записей', () => {
    it('Открыть выполненную ведомость с количеством водителей более 1001, например "Ведомость #39"', () => {
        ListStatementsPage.goTo();

        ListStatementsPage.type(ListStatementsPage.searchField, testData.statementNumber);
        ListStatementsPage.statusDropdown.click();
        ListStatementsPage.clickByStatusInStatusDropdownItems(testData.status);
        browser.pause(2000);
        ListStatementsPage.goThroughPaginations(() => false, 1, 500);

        ListStatementsPage.getStatementByNumber(testData.statementNumber).waitForDisplayed();
        const lastRowInList = $('tbody tr:last-child a');
        lastRowInList.click();
        StatementPage.waitingLoadThisPage(15_000);

        // в ведомости количество записей более 1000
        assert.isTrue(
            StatementPage
                .getColumn(1)[0]
                .getText()
                .replace(/[^\d+]/g, '') >= 1001,
        );

    });

    it('Нажать кнопку выгрузки файла', () => {
        // файл не скачивается
        assert.isTrue(!ListStatementsPage.checkSyncFileDownload(StatementPage.btnDownload.downloadIcon));
        // отображается всплывающее уведомление с текстом о недоступности выгрузки файла с более чем 1000 водителями
        assert.isTrue(StatementPage.btnDownload.downloadTooltip.isDisplayed());
    });
});
