const AutoCard = require('../../../../page/AutoCard');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Переход в карточку авто', () => {

    const DATA = {
        url: '/vehicles',
    };

    let savedCar;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goToNotEmptyCars();
    });

    it('Сохранить первую машину', () => {
        const firstCar = ReportsSummary.getCells({tr: 1, td: 1}).getText();
        [, savedCar] = firstCar.split('\n');
    });

    it('Открыть первую машину', () => {
        ReportsSummary.getCells({tr: 1, td: 1}).click();
    });

    it('Переключиться на открывшийся таб', () => {
        ReportsSummary.switchTab();
    });

    it('В табе открылась корректная страница', () => {
        expect(browser).toHaveUrlContaining(ReportsSummary.baseUrl + DATA.url);
    });

    it('В табе открылась корректная машина', () => {
        expect(AutoCard.parametersBlock.sign).toHaveAttributeEqual('value', savedCar);
    });

});
