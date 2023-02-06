const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsTransactions = require('../../../page/ReportsTransactions');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Отчет по транзакциям. Выгрузка. По водителям.', () => {

    const DATA = {
        file: 'file.csv',
        driver: {
            id: '04f646a20eb9b0b61bc640b287eb7f25',
        },
        report: [
            ['ФИО', 'Позывной', 'Условие работы', 'Статус', 'Баланс на начальную дату', 'Баланс на конечную дату', 'Бонусы', 'Наличные', 'Оплаты по карте', 'Корпоративная оплата', 'Комиссии парка', 'Комиссия сервиса', 'Платежи по поездкам парка', 'Прочие платежи парка', 'Прочие платежи сервиса', 'Промоакции', 'Чаевые'],
            ['Маверик2 Александр Отчество', 'bmw91', '4Q', 'Работает', '100,0', '100,0', '7860,0', '708,0', '0,0', '0,0', '-386,85', '-497,67', '0,0', '-6999,48', '0,0', '24,0', '0,0'],
        ],
    };

    let data;

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/group-drivers'
            + '?from=20220214T000000%2B03%3A00'
            + '&to=20220214T000000%2B03%3A00'
            + `&driver_ids=${DATA.driver.id}`,
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
