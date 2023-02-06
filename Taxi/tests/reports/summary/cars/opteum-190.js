const ReportDownloadDialog = require('../../../../page/ReportDownloadDialog');
const ReportsSummary = require('../../../../page/ReportsSummary');
const Selenoid = require('../../../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../../../utils/files');

describe('Сводные отчеты. Скачивание файла. По автомобилям', () => {

    const DATA = {
        file: 'summary_cars.csv',
        car: {
            query: 'А007АВ25',
        },
    };

    let data;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/cars?date_from=2022-01-24&date_to=2022-01-31');
    });

    it(`Ввести в поиск по машинам "${DATA.car.query}"`, () => {
        ReportsSummary.queryFilter(ReportsSummary.carFilter, DATA.car.query);
    });

    it(`В саджесте отобразилась машина "${DATA.car.query}"`, () => {
        expect(ReportsSummary.selectOption).toHaveTextStartsWith(DATA.car.query);
    });

    it(`Нажать на машину "${DATA.car.query}" в саджесте`, () => {
        ReportsSummary.selectOption[0].click();
    });

    it('В таблице отображается только выбранная машина', () => {
        expect(ReportsSummary.getCells({td: 1})).toHaveTextIncludes(DATA.car.query);
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

    it(`В сохраненном отчёте отображается корректная машина "${DATA.car.query}"`, () => {
        expect(data.pop()[1]).toContain(DATA.car.query);
    });

});
