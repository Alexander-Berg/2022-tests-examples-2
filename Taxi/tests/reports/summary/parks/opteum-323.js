const ReportsSegments = require('../../../../page/ReportsSegments');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Просмотр процента оттока', () => {

    const DATA = {
        // 7,12 % | 56,8 % | 12 %
        outflow: /^\d{1,2}(,\d{1,2})? %$/,
        filter: 'Отток водителей',
        page: '/reports/segments?segment_id=churn_rate',
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/parks');
    });

    it('В столбце оттока водителей отображаются корректные данные', () => {
        expect(ReportsSummary.getCells({td: 5})).toHaveTextMatch(DATA.outflow);
    });

    it('Нажать на процент оттока во втором месяце', () => {
        ReportsSummary.getCells({tr: 2, td: 5}).click();
    });

    it('Открылась страница сегментов водителей', () => {
        ReportsSegments.switchTab();
        expect(browser).toHaveUrlContaining(ReportsSegments.baseUrl + DATA.page);
    });

    it(`Отображается фильтр сегментов водителей "${DATA.filter}"`, () => {
        expect(ReportsSegments.segmentsFilter.input).toHaveTextEqual(DATA.filter);
    });

    it('В списке есть данные', () => {
        expect(ReportsSegments.getCells({td: 1})).toHaveTextOk();
    });

});
