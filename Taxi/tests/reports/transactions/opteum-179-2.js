const ReportsTransactions = require('../../../page/ReportsTransactions');

describe('Отчет по транзакциям. Проверка фильтров. По водителям.', () => {

    const DATA = {
        defaultType: 'По водителям',
        conditions: {
            search: 'Платный найм',
        },
    };

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/group-drivers');
    });

    it(`В режиме отображения отчёта выбран "${DATA.defaultType}"`, () => {
        expect(ReportsTransactions.filtersBlock.display.checked).toHaveTextEqual(DATA.defaultType);
    });

    it(`Ввести в дропдаун условий "${DATA.conditions.search}"`, () => {
        ReportsTransactions.queryFilter(ReportsTransactions.workConditionsFilter, DATA.conditions.search);
    });

    it(`В саджесте дропдауна отобразилась условия "${DATA.conditions.search}"`, () => {
        expect(ReportsTransactions.selectOption).toHaveTextArrayIncludes(DATA.conditions.search);
    });

    it(`Нажать на "${DATA.conditions.search}" в саджесте дропдауна условий`, () => {
        ReportsTransactions.selectOption[0].click();
    });

    it(`Отобразились транзакции с условием "${DATA.conditions.search}"`, () => {
        expect(ReportsTransactions.getCells({td: 3}))
            .toHaveTextArrayEachEqual(DATA.conditions.search, {js: true, timeout: 'long'});
    });

});
