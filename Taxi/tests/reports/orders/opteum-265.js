const DatePicker = require('../../../page/DatePicker');
const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsOrders = require('../../../page/ReportsOrders');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Отчет по заказам. Асинхронная выгрузка. Скачивание за сегодня', () => {

    const DATA = {
        file: 'report_orders.csv',
    };

    let data;

    it('Открыть страницу отчёта по заказам', () => {
        ReportsOrders.goTo();
    });

    it('Выбрать сегодняшний день в календаре', () => {
        DatePicker.open();
        DatePicker.pickToday();
        ReportsOrders.getRow().status.waitForDisplayed();
    });

    it('Нажать на кнопку скачивания отчета', () => {
        ReportsOrders.table.buttons.download.click();
    });

    it('Открылся диалог сохранения отчёта', () => {
        expect(ReportDownloadDialog.title).toHaveElemVisible();
    });

    it('Переключить кодировку на utf8', () => {
        ReportDownloadDialog.radio.utf8.click();
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportDownloadDialog.buttons.download.click();
    });

    it('Отчёт сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить отчёт', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном отчёте есть данные', () => {
        expect(data.length).toBeGreaterThan(1);
    });

});
