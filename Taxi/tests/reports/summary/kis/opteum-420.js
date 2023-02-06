const DriversBlock = require('../../../../page/DriversBlock');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводный отчёт по КИС АРТ: фильтрация водителей в отчёте по ФИО: негатив', () => {

    const DATA = {
        header: 'Водители',
        nonexist: 'Warren Ampersand',
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/kis-art?date_from=2021-11-01&date_to=2021-11-30');
    });

    it('Открыть первый отчёт', () => {
        ReportsSummary.getCells({td: 1, tr: 1}).click();
    });

    it('Отобразился сайдбар водителей', () => {
        DriversBlock.drivers.list.waitForDisplayed();
    });

    it('Ввести несуществующее имя водителя в поиск', () => {
        DriversBlock.queryFilter(DriversBlock.filter, DATA.nonexist);
    });

    it('Список водителей пустой', () => {
        expect(DriversBlock.drivers.names).not.toHaveElemExist();
    });

    it('Отобразился корректный заголовок сайдбара', () => {
        expect(DriversBlock.header).toHaveTextEqual(DATA.header);
    });

});
