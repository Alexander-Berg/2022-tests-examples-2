const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

describe('Фильтрация заявок по периоду (негатив)', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.open('/instant-payouts?date_from=2022-01-10T00%3A00&date_to=2022-01-12T23%3A59&park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru');
    });

    it('В фильтре периода указать период за который нет записей', () => {
        TransferRequests.filters.dateInput.click();
        TransferRequests.datePicker.btnEnd.click();
        TransferRequests.datePicker.btnStart.click();
        TransferRequests.datePicker.btnApply.click();
        browser.pause(1000);
    });

    it('отображается заглушка "Пока ничего нет"', () => {
        expect(TransferRequests.reportTable.notFound).toBeDisplayed();
        expect(TransferRequests.reportTable.notFound).toHaveTextEqual('Пока ничего нет');
    });

    it('Очистить фильтр', () => {
        TransferRequests.filters.dateInputBtnClear.click();
        browser.pause(1000);
        TransferRequests.getRow(1).waitForDisplayed();
    });

    it('отобразились все записи', () => {
        expect(TransferRequests.getColumn(6).length).toBeGreaterThan(1);
    });
});
