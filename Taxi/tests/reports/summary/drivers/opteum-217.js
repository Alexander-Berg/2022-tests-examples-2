const ReportDownloadDialog = require('../../../../page/ReportDownloadDialog');
const ReportsSummary = require('../../../../page/ReportsSummary');
const Selenoid = require('../../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../../utils/files');

describe('Смоук: скачать сводный отчёт', () => {

    const DATA = {
        file: 'summary_drivers.csv',
        report: [
            'ID водителя',
            'ФИО водителя',
            'Номер ВУ',
            'Позывной',
            'Условие работы',
            'Завершено заказов',
            'Всего заказов',
            'Всего заказов платформы',
            'Принято заказов',
            'Отклонено заказов водителем',
            'Отклонено заказов клиентом',
            'Время на линии',
            'Наличные',
            'Безналичные платежи',
            'Комиссия платформы',
            'Комиссия парка',
            'Прочее',
        ],
    };

    let data;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/drivers');
    });

    it('Нажать на кнопку скачивания отчета', () => {
        ReportsSummary.table.buttons.download.click();
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
