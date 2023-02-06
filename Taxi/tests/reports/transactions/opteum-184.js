const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsTransactions = require('../../../page/ReportsTransactions');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Отчет по транзакциям. Выгрузка. По датам.', () => {

    const DATA = {
        file: 'transactions_summary.csv',
        report: [
            ['Период', 'Бонусы', 'Наличные', 'Оплаты по карте', 'Корпоративная оплата', 'Комиссии партнера', 'Комиссии сервиса', 'Платежи по поездкам парка', 'Прочие платежи партнера', 'Прочие платежи сервиса', 'Промоакции', 'Чаевые'],
            ['2021-12-20T00:00:00+03:00', '1332,0', '22664,0', '5145,0', '2620,0', '-6784,62', '-2097,3', '0,0', '-101626318,4', '0,0', '3936,0', '0,0'],
        ],
    };

    let data;

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/group-dates'
            + '?from=20211220'
            + '&to=20211220',
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
