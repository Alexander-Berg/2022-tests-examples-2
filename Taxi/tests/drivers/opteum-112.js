const DriverCard = require('../../page/driverCard/DriverCard');
const ReportDownloadDialog = require('../../page/ReportDownloadDialog');
const ReportsOrders = require('../../page/ReportsOrders');
const Selenoid = require('../../../../utils/api/Selenoid');
const timeouts = require('../../../../utils/consts/timeouts');
const {csvUtf8ParseToArray} = require('../../../../utils/files');

describe('Карточка водителя: ведомость - скачать xls', () => {

    let data;

    const DATA = {
        file: 'file.csv',
        report: [
            'Дата',
            'ID водителя',
            'Водитель',
            'ID категории',
            'Категория',
            'Сумма',
            'Документ',
            'Баланс водителя',
            'Инициатор',
            'Комментарий',
        ],
    };

    it('Открыть раздел "Отчёт по заказам"', () => {
        ReportsOrders.goTo('?order_statuses=complete');
    });

    it('Перейти в карточку водителя', () => {
        const firstDriverInTable = $('tbody tr:nth-child(1) td:nth-child(3) a');
        firstDriverInTable.waitForDisplayed();
        firstDriverInTable.click();

        DriverCard.switchTab();
        DriverCard.waitingLoadThisPage(timeouts.waitUntil);
    });

    it('Открыть раздел "Ведомость"', () => {
        DriverCard.tabs.rides.click();
    });

    it('Нажать на кнопку "Скачать в формате XLS"', () => {
        const downloadInXlsBtn = $('main div[class*="TransactionsTab_filters"] button');
        downloadInXlsBtn.waitForDisplayed();
        downloadInXlsBtn.click();
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

    it('В сохраненном отчёте отображаются корректные колонки', () => {
        expect(data[0]).toEqual(DATA.report);
    });

});
