const DriversBlock = require('../../../../page/DriversBlock');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводный отчёт по КИС АРТ: фильтрация по периоду', () => {

    const DATA = {
        title: /^\d{2} водителей$/,
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/kis-art?date_from=2021-11-01&date_to=2021-11-30');
    });

    it('Открыть первый отчёт', () => {
        ReportsSummary.getCells({td: 1, tr: 1}).click();
    });

    it('Открылся сайдбар водителей', () => {
        expect(DriversBlock.header).toHaveTextMatch(DATA.title);
    });

    it('В сайдбаре есть ссылки на водителей водители', () => {
        expect(DriversBlock.drivers.links).toHaveElemLengthAbove(0);
    });

    it('В сайдбаре ссылки на водителей ведут на корректную страницу', () => {
        expect(DriversBlock.drivers.links).toHaveAttributeStartsWith('href', '/drivers/');
    });

    it('В сайдбаре корректные тексты ссылок водителей', () => {
        expect(DriversBlock.drivers.links).toHaveTextOk();
    });

});
