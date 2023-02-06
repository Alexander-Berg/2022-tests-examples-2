const ReportDownloadDialog = require('../../../../page/ReportDownloadDialog');
const ReportsSummary = require('../../../../page/ReportsSummary');
const Selenoid = require('../../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../../utils/files');

describe('Сводные отчеты. Скачивание файла. По водителям', () => {

    const DATA = {
        file: 'summary_drivers.csv',
        driver: {
            query: 'Крюков',
            table: 'Крюков-Тестович Иван, 6404917891',
            report: 'Крюков-Тестович Иван Андреевич',
        },
    };

    let data;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/drivers?date_from=20220124&date_to=20220131');
    });

    it(`Ввести в поиск по водителям "${DATA.driver.query}"`, () => {
        ReportsSummary.queryFilter(ReportsSummary.driverFilter, DATA.driver.query);
    });

    it(`В саджесте отобразился водитель "${DATA.driver.query}"`, () => {
        expect(ReportsSummary.selectOption).toHaveTextStartsWith(DATA.driver.query);
    });

    it(`Нажать на водителя "${DATA.driver.query}" в саджесте`, () => {
        ReportsSummary.selectOption[0].click();
    });

    it('В таблице отображается только выбранный водитель', () => {
        expect(ReportsSummary.getCells({td: 1})).toHaveTextEqual(DATA.driver.table);
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

    it(`В сохраненном отчёте отображаются корректный водитель "${DATA.driver.report}"`, () => {
        expect(data.pop()).toContain(DATA.driver.report);
    });

});
