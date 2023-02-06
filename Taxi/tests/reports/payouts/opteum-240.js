const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsPayouts = require('../../../page/ReportsPayouts');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Выплаты. Асинхронная выгрузка. Скачивание пустого файла', () => {

    let data;

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo(
            '?date_from=2021-01-01T01%3A48&date_to=2021-01-01T01%3A48',
            {skipWait: true},
        );
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportsPayouts.filtersBlock.report.button.click();
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
        data = Selenoid.getDownloadedFile(ReportsPayouts.report.file);
    });

    it('Распарсить отчёт', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном отчёте отображаются только названия столбцов', () => {
        expect(data).toEqual(ReportsPayouts.report.data.utf8.slice(0, 1));
    });

});
