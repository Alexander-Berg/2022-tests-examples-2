const ListStatementsPage = require('../../page/ListStatementsPage');
const {assert} = require('chai');

const testData = [
    {
        statementNumber: '2525',
        expectedRows: 1,
    },
    {
        statementNumber: '1',
    },
];

Array.from({length: testData.length}).forEach((_, i) => {
    describe('Поиск ведомости по номеру', () => {
        it('В поле поиска ввести номер ведомости', () => {
            ListStatementsPage.goTo();
            ListStatementsPage.type(ListStatementsPage.searchField, testData[i].statementNumber);
            browser.pause(2000);
            ListStatementsPage.getColumn(1)[0].waitForDisplayed();

            if ('expectedRows' in testData[i]) {
                const rows = ListStatementsPage.getColumn(1);

                assert.isTrue(
                    testData[i].expectedRows === rows.length,
                    `Не совпадает количество строк при поиске ведомости по номеру ${testData[i].statementNumber}\n
                    Expected: ${testData[i].expectedRows}\n
                    Actual: ${rows.length}`,
                );
            }

            ListStatementsPage.goThroughPaginations(rows => {
                for (let j = 1; j < rows.length; j++) {
                    assert.isTrue(
                        rows[j].getText().includes(testData[i].statementNumber),
                        `Присутствует ведомость с номером не подходящим под условие поиска\n
                        Expected: ведомости, в номере которых есть число: ${testData[i].statementNumber}\n
                        Actual: есть ведомость с номером: ${rows[j].getText()}`,
                    );
                }

                return true;
            }, 1, 500);
        });
    });
});
