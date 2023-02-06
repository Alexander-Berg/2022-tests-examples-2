const DriversBlock = require('../../../../page/DriversBlock');
const ReportDownloadDialog = require('../../../../page/ReportDownloadDialog');
const ReportsSummary = require('../../../../page/ReportsSummary');
const Selenoid = require('../../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../../utils/files');

describe('Сводный отчёт по КИС АРТ: скачивание отчёта в сайд-меню', () => {

    const DATA = {
        file: 'detailed_report.csv',
        report: [
            'Дата',
            'ФИО',
            'Телефон',
            'Статус в КИС «АРТ»',
            'КИС «АРТ» ID',
        ],
    };

    let data;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/kis-art?date_from=2021-11-01&date_to=2021-11-30');
    });

    it('Открыть первый отчёт', () => {
        ReportsSummary.getCells({td: 1, tr: 1}).click();
    });

    it('Отобразился сайдбар водителей', () => {
        DriversBlock.drivers.list.waitForDisplayed();
    });

    it('Нажать на кнопку скачивания списка', () => {
        DriversBlock.actions.button.click();
    });

    it('Открылся диалог сохранения списка', () => {
        expect(ReportDownloadDialog.title).toHaveElemVisible();
    });

    it('Переключить кодировку на utf8', () => {
        ReportDownloadDialog.radio.utf8.click();
    });

    it('Нажать на кнопку сохранения списка', () => {
        ReportDownloadDialog.buttons.download.click();
    });

    it('Список сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить список', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном списке есть данные', () => {
        expect(data.length).toBeGreaterThan(1);
    });

    it('В сохраненном списке корректные столбцы', () => {
        expect(data[0]).toEqual(DATA.report);
    });

});
