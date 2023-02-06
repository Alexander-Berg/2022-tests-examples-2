const DatePicker = require('../../../page/DatePicker');
const re = require('../../../../../utils/consts/re');
const ReportsTransactions = require('../../../page/ReportsTransactions');

describe('Отчет по транзакциям. Проверка фильтров. По датам.', () => {

    const DATA = {
        defaultType: 'По датам',
        driver: {
            search: 'Крюков',
            suggest: 'Крюков-Тестович :: Иван Андреевич',
        },
        columns: [
            'Период',
            'Наличные',
            'Оплаты по карте',
            'Корпоративная оплата',
            'Чаевые',
            'Промоакции',
            'Бонусы',
            'Комиссия сервиса',
            'Комиссии парка',
            'Прочие платежи сервиса',
            'Платежи по поездкам парка',
            'Прочие платежи парка',
        ],
        // eslint-disable-next-line no-irregular-whitespace
        numbers: /^[\d -]+,\d{2}$/,
    };

    let textsBeforeFilter;

    it('Открыть страницу отчета по транзакциям', () => {
        ReportsTransactions.goTo('/group-dates');
    });

    it(`В режиме отображения отчёта выбран "${DATA.defaultType}"`, () => {
        expect(ReportsTransactions.filtersBlock.display.checked).toHaveTextEqual(DATA.defaultType);
    });

    it('Открыть фильтр дат', () => {
        DatePicker.open();
    });

    it('Выбрать период за предыдущий месяц', () => {
        DatePicker.pickPrevMonth();
    });

    it('Отображаются корректные столбцы', () => {
        textsBeforeFilter = ReportsTransactions.getCells({td: 2}).map(elem => elem.getText());
        expect(ReportsTransactions.tableBlock.columnTitle).toHaveTextEqual(DATA.columns);
    });

    DATA.columns.forEach((column, i) => {

        it(`В столбце "${column}" отображаются корректные данные`, () => {
            expect(ReportsTransactions.getCells({td: i + 1}))
                // в первом столбце даты, в остальных цифры
                .toHaveTextMatch(i === 0 ? re.dates.one : DATA.numbers, {js: true});
        });

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

    it('Список транзакций изменился', () => {
        expect(ReportsTransactions.getCells({td: 2})).not.toHaveTextEqual(textsBeforeFilter);
    });

    it('В списке есть данные', () => {
        expect(ReportsTransactions.getCells({td: 3})).toHaveTextOk();
    });

});
