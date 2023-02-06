const ReportsSummary = require('../../../../page/ReportsSummary');

describe('Сводные отчеты. Проверка фильтров по водителям', () => {

    const DATA = {
        conditions: {
            placeholder: 'Условия работы',
            query: '4Q',
        },
        driver: {
            query: 'Крюков',
            table: 'Крюков-Тестович Иван, 6404917891',
        },
    };

    let textsBeforeFilter;

    it('Открыть страницу сводного отчёта', () => {
        ReportsSummary.goTo('/drivers?date_from=20220124&date_to=20220131');
    });

    it('Отображается фильтр условий работы', () => {
        textsBeforeFilter = ReportsSummary.getCells({td: 1}).map(elem => elem.getText());
        expect(ReportsSummary.conditionsFilter.placeholder).toHaveTextEqual(DATA.conditions.placeholder);
    });

    it(`Ввести в поиск по условиям работы "${DATA.conditions.query}"`, () => {
        ReportsSummary.queryFilter(ReportsSummary.conditionsFilter, DATA.conditions.query);
    });

    it(`В саджесте отобразились условия "${DATA.conditions.query}"`, () => {
        expect(ReportsSummary.selectOption).toHaveTextArrayEachEqual(DATA.conditions.query);
    });

    it(`Нажать на условие "${DATA.conditions.query}" в саджесте`, () => {
        ReportsSummary.selectOption.pop().click();
    });

    it('Список водителей в таблице изменился', () => {
        expect(ReportsSummary.getCells({td: 1})).not.toHaveTextEqual(textsBeforeFilter);
    });

    it('В таблице есть данные', () => {
        expect(ReportsSummary.getCells({td: 1})).toHaveTextOk();
    });

    it(`Ввести в поиск по водителям "${DATA.driver.query}"`, () => {
        ReportsSummary.queryFilter(ReportsSummary.driverFilter, DATA.driver.query);
    });

    it(`В саджесте отобразился водитель "${DATA.driver.query}"`, () => {
        expect(ReportsSummary.selectOption).toHaveTextStartsWith(DATA.driver.query);
    });

    it(`Нажать на водителя "${DATA.driver.query}" в саджесте`, () => {
        ReportsSummary.selectOption[0].click();
    });

    it('В таблице отображается только выбранный водитель', () => {
        expect(ReportsSummary.getCells({td: 1})).toHaveTextEqual(DATA.driver.table);
    });

});
