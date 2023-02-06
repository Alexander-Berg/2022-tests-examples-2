const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsPayouts = require('../../../page/ReportsPayouts');
const Selenoid = require('../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../utils/files');

describe('Выплаты. Асинхронная выгрузка. Скачивание в MacCyrillic', () => {

    let data;

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo(ReportsPayouts.report.path);
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportsPayouts.filtersBlock.report.button.click();
    });

    it('Открылся диалог сохранения отчёта', () => {
        expect(ReportDownloadDialog.title).toHaveElemVisible();
    });

    it('Переключить кодировку на mac', () => {
        ReportDownloadDialog.radio.mac.click();
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

    it('В сохраненном отчёте отображаются корректные данные', () => {
        expect(data.slice(0, ReportsPayouts.report.data.other.length))
            .toEqual(ReportsPayouts.report.data.other);
    });

});
