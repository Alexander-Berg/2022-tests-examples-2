const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const testData = {
    pageCounter: 2,
    paginationValues: ['25', '50', '75', '100'],
};

let driverNames = [];

Array.from({length: testData.paginationValues.length}).forEach((_, i) => {
    describe('Пагинация: количество элементов в списке на страницу', () => {
        it('Открыть страницу водителей', () => {
            DriversPage.goTo();
        });

        it('Проверить пагинацию', () => {
            // установить количество строк на странице пагинации
            DriversPage.paginations.maxRowsDropdown.waitForDisplayed();
            DriversPage.paginations.maxRowsDropdown.click();
            browser.pause(250);
            DriversPage.selectDropdownItem(testData.paginationValues[i]);
            browser.pause(2000);

            let pageCounter = 0;

            DriversPage.goThroughPaginations(rows => {
                // проверяем, что количество строк в выдаче соответствует установленному количеству строк
                assert.equal(rows.length - 1, testData.paginationValues[i]);

                // первая страница - записываем имена водителей
                if (pageCounter === 0) {
                    driverNames = [];

                    for (let j = 0; j < rows.length - 1; j++) {
                        driverNames[j] = rows[j].getText();
                    }

                    pageCounter++;
                    return false;
                }

                // для всех остальных страниц - сравниваем, что не все имена на странице совпадают
                // (т.к. может присутствовать какое-то количество водителей с одинаковыми именами)
                let equalNames = 0;

                for (let j = 0; j < rows.length - 1; j++) {
                    if (rows[j].getText() === driverNames[j]) {
                        equalNames++;
                    }

                    // записываем имена водителей для сравнения на следующей странице
                    driverNames[j] = rows[j].getText();
                }

                assert.notEqual(equalNames, testData.paginationValues[i]);

                pageCounter++;
                return testData.pageCounter <= pageCounter;
            }, 4, 2000);
        });
    });
});
