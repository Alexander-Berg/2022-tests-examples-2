const DriverCard = require('../../page/driverCard/DriverCard');
const OrdersTab = require('../../page/driverCard/OrdersTab');
const ReportsOrders = require('../../page/ReportsOrders');
const {assert} = require('chai');

describe('Карточка водителя: фильтрация в табе "Заказы"', () => {

    const testData = {
        orderType: 'Безналичный',
        status: 'Отменён',
        paymentType: 'Безналичные',
    };

    const timeToWaitElem = 30_000;
    let allOrdersLength;

    it('Перейти на страницу отчёта по заказам', () => {
        ReportsOrders.goTo();
    });

    it('Перейти на страницу водителя', () => {
        const firstDriverInTable = $('tbody tr:nth-child(1) td:nth-child(3) a');

        firstDriverInTable.waitForDisplayed({timeout: timeToWaitElem});
        firstDriverInTable.click();

        DriverCard.switchTab();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('Открыть "Заказы" в карточке водителя', () => {
        DriverCard.tabs.transactions.click();

        const firstRowInTable = $('tbody tr:nth-child(1)');
        firstRowInTable.waitForDisplayed({timeout: timeToWaitElem});

        browser.pause(1000);
        allOrdersLength = $$('tbody tr').length;
    });

    it('Проверить фильтрацию', () => {
        const btnClear = $('div[class*="OrdersTab_filters"] div.Select__control button');

        for (const filter in OrdersTab.filters) {
            OrdersTab.filters[filter].waitForDisplayed({timeout: timeToWaitElem});
            OrdersTab.filters[filter].click();

            OrdersTab.selectDropdownItem(testData[filter]);
            browser.keys('Escape');
            browser.pause(2000);

            assert.isTrue(allOrdersLength >= $$('tbody tr').length);

            btnClear.waitForDisplayed({timeout: timeToWaitElem});
            btnClear.click();
            browser.keys('Escape');
        }
    });
});
