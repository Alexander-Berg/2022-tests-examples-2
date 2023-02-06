const DriversBlock = require('../../../../page/DriversBlock');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводный отчёт по КИС АРТ: фильтрация водителей в отчёте по ФИО', () => {

    const DATA = {
        header: '1 водитель',
    };

    let driver;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/kis-art?date_from=2021-11-01&date_to=2021-11-30');
    });

    it('Открыть первый отчёт', () => {
        ReportsSummary.getCells({td: 1, tr: 1}).click();
    });

    it('Отобразился сайдбар водителей', () => {
        DriversBlock.drivers.list.waitForDisplayed();
    });

    it('Сохранить имя первого водителя', () => {
        driver = DriversBlock.drivers.names[0].getText();
    });

    it('Ввести имя сохраненного водителя в поиск', () => {
        DriversBlock.queryFilter(DriversBlock.filter, driver);
    });

    it('Отобразился только один запрошенный водитель', () => {
        expect(DriversBlock.drivers.names).toHaveTextEqual(driver, {js: true});
    });

    it('Отобразился корректный заголовок сайдбара', () => {
        expect(DriversBlock.header).toHaveTextEqual(DATA.header);
    });

});
