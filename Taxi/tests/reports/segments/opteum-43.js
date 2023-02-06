const DriverCard = require('../../../page/driverCard/DriverCard');
const ReportsSegments = require('../../../page/ReportsSegments');

describe('Фильтр: указание условий работы', () => {

    const DATA = {
        default: 'Все условия работы',
        query: '4Q',
    };

    let elemsBeforeFilter;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Отображается фильтр условий работы', () => {
        elemsBeforeFilter = ReportsSegments.getCells({td: 1});
        expect(ReportsSegments.conditionsFilter.placeholder).toHaveTextEqual(DATA.default);
    });

    it(`Ввести в поиск по условиям работы "${DATA.query}"`, () => {
        ReportsSegments.queryFilter(ReportsSegments.conditionsFilter, DATA.query);
    });

    it(`В саджесте отобразились условия "${DATA.query}"`, () => {
        expect(ReportsSegments.selectOption).toHaveTextArrayEachEqual(DATA.query);
    });

    it(`Нажать на условие "${DATA.query}" в саджесте`, () => {
        ReportsSegments.selectOption[1].click();
    });

    it('Список водителей изменился', () => {
        expect(ReportsSegments.getCells({td: 1})).not.toHaveElemEqual(elemsBeforeFilter);
    });

    it('В списке есть данные', () => {
        expect(ReportsSegments.getCells({td: 1})).toHaveTextOk();
    });

    it('Открыть первого водителя из списка', () => {
        ReportsSegments.getCells({td: 1, tr: 1}).click();
    });

    it(`В карточке водителя отображается условие работы "${DATA.query}"`, () => {
        ReportsSegments.switchTab();
        expect(DriverCard.selects.single).toHaveTextArrayIncludes(DATA.query, {timeout: 'long'});
    });

});
