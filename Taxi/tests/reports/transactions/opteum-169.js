const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsTransactions = require('../../../page/ReportsTransactions');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Отчет по транзакциям. Выгрузка. Список.', () => {

    const DATA = {
        file: 'driver_transactions.csv',
        driver: {
            id: '914539e0aee64dda3d38a99726f974f3',
        },
        report: [
            ['Дата', 'ID водителя', 'Водитель', 'ID категории', 'Категория', 'Сумма', 'Документ', 'Инициатор', 'Комментарий'],
            ['29.04.2021 20:40:20', '914539e0aee64dda3d38a99726f974f3', 'Крюков-Тестович Иван Андреевич', 'partner_ride_card', 'Оплата картой, поездка партнера', '-10,0', 'Order #457bf059c85648af8611dde13e8de736', 'Platform', 'Оплата картой, поездка партнера'],
            ['28.04.2021 17:00:00', '914539e0aee64dda3d38a99726f974f3', 'Крюков-Тестович Иван Андреевич', 'partner_service_recurring_payment', 'Платежи по расписанию', '-100,0', '—', 'Platform', 'Списание №415'],
        ],
    };

    let data;

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/list'
            + '?from=20210428'
            + '&to=20210430'
            + `&driver_id=${DATA.driver.id}`,
        );
    });

    it('Дождаться отображения таблицы', () => {
        ReportsTransactions.getCells({td: 1, tr: 1}).waitForDisplayed();
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportsTransactions.filtersBlock.report.button.click();
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

    it('В сохраненном отчёте отображаются корректные данные', () => {
        expect(data).toEqual(DATA.report);
    });

});
