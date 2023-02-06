const DriverCard = require('../../../../page/driverCard/DriverCard');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Переход в карточку водителя', () => {

    let name;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/drivers');
    });

    it('Сохранить имя первого водителя из списка', () => {
        [name] = ReportsSummary
            .getCells({tr: 1, td: 1})
            .getText()
            .split(', ');
    });

    it('Открыть первого водителя из списка', () => {
        ReportsSummary.getCells({tr: 1, td: 1}).click();
    });

    it('Переключиться на открывшийся таб водителя', () => {
        ReportsSummary.switchTab();
    });

    it('В карточке водителя отображается корректное имя', () => {
        expect(DriverCard.title).toHaveTextEqual(name);
    });

});
