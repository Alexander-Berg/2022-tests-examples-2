const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Фильтрация по водителю', () => {
    let driver;

    it('Открыть страницу отчёт по заказам 349', () => {
        ReportsOrders.goTo();
    });

    it('В фильтр "Водитель" ввести имя водителя из списка', () => {
        driver = ReportsOrders.getRow(2).driver.getText();
        ReportsOrders.filtersList.driver.click();
        ReportsOrders.focusedInput.addValue(driver);
        browser.pause(1000);
        browser.keys('Enter');
        browser.pause(1000);
    });

    it('В списке отобразились заказы только этого водителя', () => {
        ReportsOrders.allRows.driver.forEach(currentRowDriver => {
            assert.equal(currentRowDriver.getText(), driver);
        });
    });
});
