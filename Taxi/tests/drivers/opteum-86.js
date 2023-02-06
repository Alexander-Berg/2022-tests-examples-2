const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 5000;
const driverName = 'madworld';

describe('Заглушка при отсутствии результатов поиска', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it(`В строке поиска ввести ${driverName}`, () => {
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        assert.isTrue(DriversPage.reportTable.notFound.waitForDisplayed({timeout: timeToWaitElem}));
    });
});
