const ReportsSummary = require('../../../../page/ReportsSummary');
const TooltipBlock = require('../../../../page/TooltipBlock');

const getSuccessfulRe = orders => new RegExp(`Успешно завершены: ${orders}( (\\d+%))?`);

describe('Просмотр информации по заказам водителя (сотрудником парка)', () => {

    let orders;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/drivers');
    });

    it('В столбце успешно завершенных заказов отображается корректное число', () => {
        expect(ReportsSummary.getCells({td: 3})).toHaveTextNumberAboveOrEqual(0);
    });

    it('Нажать на успешно завершенные заказы у первого водителя', () => {
        const elem = ReportsSummary.getCells({tr: 1, td: 3});

        orders = elem.getText();
        elem.$('span').click();
    });

    it('Отобразился тултип', () => {
        expect(TooltipBlock.texts).toHaveElemVisible();
    });

    it('В тултипе отображается корректная строка с количеством завершенных заказов', () => {
        expect(TooltipBlock.texts).toHaveTextArrayIncludesMatch(getSuccessfulRe(orders));
    });

});
