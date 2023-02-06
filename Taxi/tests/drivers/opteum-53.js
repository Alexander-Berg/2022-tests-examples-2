const DriversPage = require('../../page/DriversPage');

const testData = [
    {
        number: '70001259596',
        drivers: 1,
    },
    {
        number: '7000125959',
        drivers: 5,
    },
];

const searchByNumber = number => {
    DriversPage.clearWithBackspace(DriversPage.searchField);
    DriversPage.searchField.setValue(number);
    browser.pause(2000);
};

describe('Поиск водителя по номеру телефона', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    for (const data of testData) {
        it(`В строке поиска указать номер телефона водителя ${data.number}`, () => {
            DriversPage.searchField.waitForDisplayed();
            searchByNumber(data.number);
        });

        it(`в списке водителей отобразилось количество водителей равное ${data.drivers}`, () => {
            expect($$('table tbody >tr')).toHaveElemLengthEqual(data.drivers);
        });

        it('телефон водителя соответствует введенному в поиске', () => {
            expect(DriversPage.getColumnInTable().phone).toHaveTextIncludes(data.number);
        });
    }
});
