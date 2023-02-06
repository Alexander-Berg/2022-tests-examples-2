const DriversPage = require('../../page/DriversPage');

describe('Фильтрация водителей по состоянию', () => {

    const testData = [
        {state: 'Офлайн'},
        {state: 'Свободный'},
        {state: 'На линии'},
    ];

    const maxPageAmount = 5;

    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
        DriversPage.statusesDropdown.waitForDisplayed({timeout: 5000});
    });

    for (const {state} of testData) {
        it(`Проверить фильтрацию по состоянию "${state}"`, () => {
            DriversPage.statusesDropdown.click();
            DriversPage.selectDropdownItem(state);
            browser.pause(2000);

            if (state === 'На линии') {
                let statusCounter = 0;

                const statusesDict = {
                    'Занят': false,
                    'Свободный': false,
                    'На заказе': false,
                };

                DriversPage.goThroughPaginations(
                    rows => {
                        for (let j = 0; j < rows.length - 1; j++) {
                            if (
                                rows[j].getText() in statusesDict
                                && !statusesDict[rows[j].getText()]
                            ) {
                                statusesDict[rows[j].getText()] = true;
                                statusCounter += 1;
                            }
                        }

                        return statusCounter > 1;
                    },
                    2,
                    2000,
                );

                expect(statusCounter).toBeGreaterThan(1);
            } else {
                let pageCounter = 0;

                DriversPage.goThroughPaginations(
                    rows => {
                        for (let j = 0; j < rows.length - 1; j++) {
                            expect(rows[j]).toHaveTextEqual(state);
                        }

                        pageCounter += 1;
                        return pageCounter === maxPageAmount;
                    },
                    2,
                    2000,
                );
            }
        });
    }

});
