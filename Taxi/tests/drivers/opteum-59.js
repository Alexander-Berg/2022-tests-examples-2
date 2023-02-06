const DriversPage = require('../../page/DriversPage');

describe('Фильтрация водителей по условиям работы', () => {

    const testData = [
        {driverTerms: '4Q'},
        {driverTerms: 'Yandex'},
        {driverTerms: 'Все условия работы'},
    ];

    const maxPageAmount = 5;

    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    for (const {driverTerms} of testData) {
        it(`Проверить фильтрацию по условию работы "${driverTerms}"`, () => {
            DriversPage.statusesDropdown.waitForDisplayed({timeout: 5000});

            DriversPage.workConditionsDropdown.click();
            DriversPage.selectDropdownItem(driverTerms);
            browser.pause(2000);

            if (driverTerms === 'Все условия работы') {
                let statusCounter = 0;

                const statusesDict = {
                    '4Q': false,
                    'Yandex': false,
                };

                DriversPage.goThroughPaginations(
                    rows => {
                        for (let j = 0; j < rows.length - 1; j++) {
                            if (rows[j].getText() in statusesDict) {
                                if (!statusesDict[rows[j].getText()]) {
                                    statusesDict[rows[j].getText()] = true;
                                    statusCounter += 1;
                                }
                            } else {
                                statusesDict[rows[j].getText()] = false;
                            }
                        }

                        return statusCounter > 1;
                    },
                    6,
                    2000,
                );

                expect(statusCounter).toBeGreaterThan(1);
            } else {
                let pageCounter = 0;

                DriversPage.goThroughPaginations(
                    rows => {
                        for (let j = 0; j < rows.length - 1; j++) {
                            expect(rows[j]).toHaveTextEqual(driverTerms);
                        }

                        pageCounter += 1;
                        return pageCounter === maxPageAmount;
                    },
                    6,
                    2000,
                );
            }
        });
    }

});
