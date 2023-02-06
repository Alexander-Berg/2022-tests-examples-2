const DriversPage = require('../../page/DriversPage');

describe('Фильтрация водителей по статусу', () => {

    const testData = [
        {status: 'Не работает'},
        {status: 'Уволен'},
        {status: 'Работает'},
    ];

    const maxPageAmount = 5;

    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
        DriversPage.statusesDropdown.waitForDisplayed({timeout: 5000});
    });

    for (const {status} of testData) {
        it(`Проверить фильтрацию по статусу "${status}"`, () => {
            DriversPage.statusesDropdown.click();
            DriversPage.selectDropdownItem(status);
            browser.pause(2000);

            let pageCounter = 0;

            DriversPage.goThroughPaginations(
                rows => {
                    for (let j = 0; j < rows.length - 1; j++) {
                        expect(rows[j]).toHaveTextEqual(status);
                    }

                    pageCounter += 1;
                    return pageCounter === maxPageAmount;
                },
                1,
                2000,
            );
        });
    }

});
