const ReportsSegments = require('../../../page/ReportsSegments');

describe('Фильтр: указание дней без заказов', () => {

    const DATA = {
        dropdowns: [
            {
                name: 'от 5 до 10 дней',
                index: 0,
            },
            {
                name: 'от 10 до 20 дней',
                index: 1,
            },
            {
                name: 'более 40 дней',
                index: 3,
            },
            {
                name: 'Текущий месяц',
                index: 4,
            },
        ],
    };

    const defaultName = DATA.dropdowns[0].name;

    let textsBeforeFilter;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it(`Отображается фильтр дней без заказов "${defaultName}"`, () => {
        expect(ReportsSegments.daysFilter.input).toHaveTextEqual(defaultName);
    });

    DATA.dropdowns.reverse().forEach(({name, index}) => {

        it(`Выбрать в фильтре дней без заказов "${name}"`, () => {
            textsBeforeFilter = ReportsSegments.getCells({td: 2}).map(elem => elem.getText());

            ReportsSegments.daysFilter.input.click();
            ReportsSegments.selectOption[index].click();
        });

        it('Список водителей изменился', () => {
            expect(ReportsSegments.getCells({td: 2})).not.toHaveTextEqual(textsBeforeFilter);
        });

        it('В списке есть данные', () => {
            expect(ReportsSegments.getCells({td: 1})).toHaveTextOk();
        });

        it(`Отображается выбранный фильтр дней без заказов "${name}"`, () => {
            expect(ReportsSegments.daysFilter.input).toHaveTextEqual(name);
        });

    });

});
