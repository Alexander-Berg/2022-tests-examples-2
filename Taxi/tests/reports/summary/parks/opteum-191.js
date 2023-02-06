const ReportDownloadDialog = require('../../../../page/ReportDownloadDialog');
const ReportsSummary = require('../../../../page/ReportsSummary');
const Selenoid = require('../../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../../utils/files');

describe('Сводные отчеты. Скачивание файла. По датам', () => {

    const DATA = {
        // 2022-10 | 2021-12 | 2019-07
        date: /^20[12]\d-[01]\d$/,
        file: 'summary_parks.csv',
        report: [
            'Месяц',
            'Активные автомобили',
            'Активные водители',
            'Завершено заказов',
            'Всего заказов',
            'Всего заказов платформы',
            'Принято заказов',
            'Отклонено заказов водителем',
            'Отклонено заказов клиентом',
            'Новые водители',
            'Отток водителей',
            'Время на линии',
            'Среднее время водителя на линии',
            'Среднее время авто на линии',
            'Наличные',
            'Безналичные',
            'Комиссия платформы',
            'Комиссия парка',
            'Дополнительная плата за программное обеспечение',
            'Услуги по привлечению водителей',
            'Услуга по возврату водителей',
        ],
    };

    let data;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/parks');
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

    it('В первой колонке сохраненного отчёта даты', () => {
        data.slice(1).forEach(row => expect(row[0]).toMatch(DATA.date));
    });

});
