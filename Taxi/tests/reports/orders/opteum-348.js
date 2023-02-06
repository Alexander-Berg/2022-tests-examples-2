const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Фильтрация по периоду', () => {
    let day;

    it('Открыть страницу отчёт по заказам 348', () => {
        ReportsOrders.open('/reports/orders?date_from=20220204T000000%2B03%3A00&date_to=20220206T235900%2B03%3A00');
    });

    it('Установить определённый период 348', () => {
        ReportsOrders.filtersList.datePicker.click();
        ReportsOrders.datePicker.btnStart.click();
        ReportsOrders.datePicker.btnStart.click();

        day = ReportsOrders.datePickerSelectedDate.getValue().replace(/ 20.. г./, '');

        ReportsOrders.datePickerConfirmButton.click();
        ReportsOrders.getRow().status.waitForDisplayed();
    });

    it('Отобразились заказы только в этом периоде 348', () => {
        ReportsOrders.allRows.pickupDate.forEach((row, i) => {
            if (i >= 40) {
                return;
            }

            assert.isTrue(row.getText().includes(day));
        });
    });
});
