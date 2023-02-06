const ReportsOrders = require('../../../../page/ReportsOrders');
const ReportsSummary = require('../../../../page/ReportsSummary');
const TooltipBlock = require('../../../../page/TooltipBlock');

describe('Просмотр количественной информации о заказах по конкретному водителю за выбранный период', () => {

    const DATA = {
        path: '/reports/orders',
        driver: 'Крюков',
    };

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/parks');
    });

    it('Нажать на завершенные заказы во втором месяце', () => {
        ReportsSummary.getCells({tr: 2, td: 6}).$('span').click();
    });

    it('Отобразился тултип с информацией', () => {
        expect(TooltipBlock.texts).toHaveElemVisible();
    });

    it('Нажать на ссылку списка заказов в тултипе', () => {
        TooltipBlock.links[0].click();
    });

    it(`Открылась страница "${DATA.path}"`, () => {
        ReportsSummary.switchTab();
        expect(browser).toHaveUrlContaining(ReportsSummary.baseUrl + DATA.path);
    });

    it(`В фильтре водителя ввести имя "${DATA.driver}"`, () => {
        ReportsOrders.filtersList.driver.click();
        ReportsOrders.focusedInput.setValue(DATA.driver);
    });

    it(`В саджесте отобразился водитель "${DATA.driver}"`, () => {
        expect(ReportsOrders.selectOption).toHaveTextStartsWith(DATA.driver);
    });

    it(`Нажать на водителя "${DATA.driver}" в саджесте`, () => {
        ReportsOrders.selectOption[0].click();
    });

    it(`Отобразились транзакции только водителя "${DATA.driver}"`, () => {
        expect(ReportsOrders.getCells({td: 3})).toHaveTextStartsWith(DATA.driver);
    });

});
