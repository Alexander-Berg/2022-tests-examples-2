const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Фильтрация по дате подачи', () => {
    let day;

    it('Открыть страницу отчёт по заказам 346', () => {
        ReportsOrders.open('/reports/orders?date_from=20220204T000000%2B03%3A00&date_to=20220206T235900%2B03%3A00');
    });

    it('Установить определённый период 346', () => {
        ReportsOrders.filtersList.datePicker.click();
        ReportsOrders.datePicker.btnStart.click();
        ReportsOrders.datePicker.btnStart.click();

        day = ReportsOrders.datePickerSelectedDate.getValue().replace(/ 20.. г./, '');

        ReportsOrders.datePickerConfirmButton.click();
        ReportsOrders.getRow().status.waitForDisplayed();
    });

    it('Выставить фильтр по дате подачи 346', () => {
        ReportsOrders.filtersList.date.click();
        ReportsOrders.date.pickupDate.click();
        browser.pause(300);
    });

    it('Отобразились заказы только в этом периоде 346', () => {
        ReportsOrders.allRows.pickupDate.forEach((row, i) => {
            if (i >= 40) {
                return;
            }

            assert.isTrue(row.getText().includes(day));
        });
    });
});
