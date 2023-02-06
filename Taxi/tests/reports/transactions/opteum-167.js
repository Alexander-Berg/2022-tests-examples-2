const ReportsTransactions = require('../../../page/ReportsTransactions');

describe('Отчет по транзакциям. Проверка фильтров. Список.', () => {

    const DATA = {
        defaultType: 'Список',

        date: /^27 апр., (?:\d{1,2}:){2}\d{1,2}$/,
        driver: {
            search: 'Крюков',
            suggest: 'Крюков-Тестович :: Иван Андреевич',
            table: 'Крюков-Тестович Иван Андреевич',
        },
        order: {
            search: '141758',
            driver: 'Лукин Богдан Александрович',
            count: 3,
        },
        category: {
            search: 'Наличные',
        },
    };

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/list'
            + '?from=20210427'
            + '&to=20210427',
        );
    });

    it(`Отобразились транзакции только за дату "${DATA.date}"`, () => {
        expect(ReportsTransactions.getCells({td: 1})).toHaveTextMatch(DATA.date);
    });

    it(`В режиме отображения отчёта выбран "${DATA.defaultType}"`, () => {
        expect(ReportsTransactions.filtersBlock.display.checked).toHaveTextEqual(DATA.defaultType);
    });

    it(`Ввести в поиск по водителям "${DATA.driver.search}"`, () => {
        ReportsTransactions.queryFilter(ReportsTransactions.driverFilter, DATA.driver.search);
    });

    it(`В саджесте отобразился водитель "${DATA.driver.search}"`, () => {
        expect(ReportsTransactions.selectOption).toHaveTextStartsWith(DATA.driver.suggest);
    });

    it(`Нажать на водителя "${DATA.driver.search}" в саджесте`, () => {
        ReportsTransactions.selectOption[0].click();
    });

    it(`Отобразились транзакции только водителя "${DATA.driver.suggest}"`, () => {
        expect(ReportsTransactions.getCells({td: 2})).toHaveTextArrayEachEqual(DATA.driver.table);
    });

    it('Очистить поиск водителя', () => {
        ReportsTransactions.driverFilter.erase.click();
    });

    it(`Ввести в поиск по заказам "${DATA.order.search}"`, () => {
        ReportsTransactions.queryFilter(ReportsTransactions.orderFilter, DATA.order.search);
    });

    it(`Отобразились "${DATA.order.count}" транзакции с заказом "${DATA.order.search}"`, () => {
        expect(ReportsTransactions.getCells({td: 2})).toHaveElemLengthEqual(DATA.order.count);
        expect(ReportsTransactions.getCells({td: 2})).toHaveTextArrayEachEqual(DATA.order.driver);
        expect(ReportsTransactions.getCells({td: 5})).toHaveTextArrayEachEqual(DATA.order.search);
    });

    it('Очистить поиск заказа', () => {
        ReportsTransactions.orderFilter.erase.click();
    });

    it(`Ввести в дропдаун категорий "${DATA.category.search}"`, () => {
        ReportsTransactions.queryFilter(ReportsTransactions.categoryFilter, DATA.category.search);
    });

    it(`В саджесте дропдауна отобразилась категория "${DATA.category.search}"`, () => {
        expect(ReportsTransactions.selectOption).toHaveTextArrayIncludes(DATA.category.search);
    });

    it(`Нажать на "${DATA.category.search}" в саджесте дропдауна категорий`, () => {
        ReportsTransactions.selectOption[0].click();
    });

    it(`Отобразились транзакции с категорией "${DATA.category.search}"`, () => {
        expect(ReportsTransactions.getCells({td: 3})).toHaveTextArrayEachEqual(DATA.category.search);
    });

});
