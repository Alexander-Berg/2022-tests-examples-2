const ReportsOrders = require('../../../page/ReportsOrders');
const {assert} = require('chai');

describe('Фильтрация по дате завершения', () => {
    let day;

    it('Открыть страницу отчёт по заказам 347', () => {
        ReportsOrders.open('/reports/orders?date_from=20220204T000000%2B03%3A00&date_to=20220206T235900%2B03%3A00');
    });

    it('Установить определённый период 347', () => {
        ReportsOrders.filtersList.datePicker.click();
        ReportsOrders.datePicker.btnStart.click();
        ReportsOrders.datePicker.btnStart.click();

        day = ReportsOrders.datePickerSelectedDate.getValue().replace(/ 20.. г./, '');

        ReportsOrders.datePickerConfirmButton.click();
        ReportsOrders.getRow().status.waitForDisplayed({timeout: 50_000});
    });

    it('Выставить фильтр по дате завершения 347', () => {
        ReportsOrders.filtersList.date.click();
        ReportsOrders.date.completionDate.click();
        browser.pause(300);
        ReportsOrders.getRow().status.waitForDisplayed({timeout: 50_000});
    });

    it('Отобразились заказы только в этом периоде 347', () => {
        ReportsOrders.allRows.completionDate.forEach((row, i) => {
            if (i >= 40) {
                return;
            }

            assert.isTrue(row.getText().includes(day));
        });
    });
});
