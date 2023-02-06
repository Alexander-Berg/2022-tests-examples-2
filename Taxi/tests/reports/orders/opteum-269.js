const NotificationsBlock = require('../../../page/NotificationsBlock');
const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsOrders = require('../../../page/ReportsOrders');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Отчет по заказам. Асинхронная выгрузка. Скачивание файла из уведомления', () => {

    const DATA = {
        toast: 'Запрос на формирование отчета принят. '
             + 'Ссылка для скачивания придёт вам на почту и в уведомления Диспетчерской',
        notify: 'Файл "Отчет по заказам" готов',
        file: 'report_orders.csv',
    };

    let data;

    it('Открыть страницу отчёта по заказам', () => {
        ReportsOrders.goTo();
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

    it('Отобразилось сообщение о запросе отчёта', () => {
        expect(ReportDownloadDialog.toast).toHaveTextEqual(DATA.toast, {timeout: 'long'});
    });

    it('Скачать отчёт из уведомления', () => {
        NotificationsBlock.downloadReportByName(DATA.notify);
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
