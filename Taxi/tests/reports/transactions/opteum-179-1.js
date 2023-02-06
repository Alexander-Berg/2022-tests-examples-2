const ReportsTransactions = require('../../../page/ReportsTransactions');

describe('Отчет по транзакциям. Проверка фильтров. По водителям.', () => {

    const DATA = {
        defaultType: 'По водителям',
        driver: {
            search: 'Крюков',
            suggest: 'Крюков-Тестович :: Иван Андреевич',
            table: 'Крюков-Тестович Иван Андреевич',
        },
        status: {
            search: 'Не работает',
            notFound: 'Тут ничего нет',
        },
    };

    let notFound, textsBeforeFilter;

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/group-drivers');
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
        expect(ReportsTransactions.getCells({td: 1}))
            .toHaveTextArrayEachEqual(DATA.driver.table, {js: true, timeout: 'long'});
    });

    it('Очистить поиск водителя', () => {
        ReportsTransactions.driverFilter.erase.click();
    });

    it(`Ввести в дропдаун статуса "${DATA.status.search}"`, () => {
        ReportsTransactions.queryFilter(ReportsTransactions.driverStatusFilter, DATA.status.search);
    });

    it(`В саджесте дропдауна отобразился статус "${DATA.status.search}"`, () => {
        expect(ReportsTransactions.selectOption).toHaveTextEqual(DATA.status.search);
    });

    it(`Нажать на "${DATA.status.search}" в саджесте дропдауна статуса`, () => {
        textsBeforeFilter = ReportsTransactions.getCells({td: 1}).map(elem => elem.getText());
        ReportsTransactions.selectOption[0].click();
    });

    it('Список транзакций изменился', () => {
        // если под статус не попал ни один водитель
        if (ReportsTransactions.reportTable.notFound.isDisplayed()) {
            notFound = true;
        } else {
            expect(ReportsTransactions.getCells({td: 1}))
                .not.toHaveTextEqual(textsBeforeFilter, {js: true, timeout: 'long'});
        }
    });

    it('В списке есть данные или заглушка', () => {
        if (notFound) {
            return expect(ReportsTransactions.reportTable.notFound).toHaveTextEqual(DATA.status.notFound);
        }

        expect(ReportsTransactions.getCells({td: 3})).toHaveTextOk();
    });

});
