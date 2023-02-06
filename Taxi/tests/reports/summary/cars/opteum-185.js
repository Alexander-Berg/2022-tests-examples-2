const AutoCard = require('../../../../page/AutoCard');
const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводные отчеты. Проверка фильтров по автомобилям', () => {

    const DATA = {
        rent: 'Только арендные',
        url: '/vehicles',
        parkSelect: 'Да',
    };

    let savedCars;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goToNotEmptyCars();
    });

    it('Сохранить текущие машины', () => {
        savedCars = ReportsSummary.getCells({td: 1}).map(elem => elem.getText());
    });

    it(`Отображается чекбокс "${DATA.rent}"`, () => {
        expect(ReportsSummary.rentFilter.label).toHaveTextEqual(DATA.rent);
    });

    it(`Поставить чекбокс "${DATA.rent}"`, () => {
        ReportsSummary.rentFilter.checkbox.click();
    });

    it('Машины в таблице изменились', () => {
        expect(ReportsSummary.getCells({td: 1})).not.toHaveTextEqual(savedCars);
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

    it('У машины выбран селект парковой машины', () => {
        expect(AutoCard.parametersBlock.park).toHaveTextEqual(DATA.parkSelect);
    });

});
