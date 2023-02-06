const ListStatementsPage = require('../../page/ListStatementsPage');
const timeouts = require('../../../../utils/consts/timeouts');
const {assert} = require('chai');

const testData = [
    {
        status: ListStatementsPage.statuses.preparing,
        result: {
            'Подготовка': true,
            'Черновик': false,
            'В работе': false,
            'Обработана': false,
        },
    },
    {
        status: ListStatementsPage.statuses.draft,
        result: {
            'Подготовка': false,
            'Черновик': true,
            'В работе': false,
            'Обработана': false,
        },
    },
    {
        status: ListStatementsPage.statuses.executed,
        result: {
            'Подготовка': false,
            'Черновик': false,
            'В работе': false,
            'Обработана': true,
        },
    },
    {
        status: ListStatementsPage.statuses.allStatuses,
        result: {
            'Подготовка': true,
            'В работе': true,
            'Черновик': true,
            'Обработана': true,
        },
    },
];

describe('Фильтрация ведомостей по статусу', () => {

    for (const {status, result} of testData) {

        it(`Проверить фильтрацию по статусу "${status}"`, () => {
            ListStatementsPage.goTo();

            ListStatementsPage.statusDropdown.click();
            ListStatementsPage.clickByStatusInStatusDropdownItems(status);
            browser.pause(500);

            try {
                ListStatementsPage.getRowInTable(1).status.waitForDisplayed({timeout: timeouts.waitUntilShort});
            } catch {
                ListStatementsPage.reportTable.notFound.waitForDisplayed({timeout: timeouts.waitUntilShort});
                return assert.isTrue(ListStatementsPage.getColumn(1).length === 0);
            }

            const statusesCounter = {
                'Подготовка': false,
                'В работе': false,
                'Черновик': false,
                'Обработана': false,
            };

            const maxPageForPaginations = 5;
            let pageCounter = 1;

            ListStatementsPage.goThroughPaginations(
                rows => {
                    for (const row of rows) {
                        if (
                            row.getText() in statusesCounter
                            && !statusesCounter[row.getText()]
                        ) {
                            statusesCounter[row.getText()] = true;
                        }
                    }

                    pageCounter += 1;
                    return pageCounter === maxPageForPaginations;
                },
                2,
                1000,
            );

            if (status === ListStatementsPage.statuses.allStatuses) {
                let trueCounter = 0;

                for (const count in statusesCounter) {
                    if (statusesCounter[count]) {
                        trueCounter += 1;
                    }
                }

                assert.isTrue(trueCounter > 1);
            } else {
                for (const count in statusesCounter) {
                    assert.equal(statusesCounter[count], result[count]);
                }
            }
        });
    }
});
