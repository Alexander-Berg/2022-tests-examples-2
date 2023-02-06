const ReportDownloadDialog = require('../../../page/ReportDownloadDialog');
const ReportsPayouts = require('../../../page/ReportsPayouts');

describe('Выплаты. Асинхронная выгрузка. Проверка ограничения в 90 дней', () => {

    const DATA = {
        toast: 'Максимальный период 90 дней',
    };

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo('?date_from=2021-01-01T01%3A48&date_to=2021-04-02T01%3A48');
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportsPayouts.filtersBlock.report.button.click();
    });

    it('Отобразилось сообщение о превышении количества дней', () => {
        expect(ReportDownloadDialog.toast).toHaveTextEqual(DATA.toast);
    });

});
