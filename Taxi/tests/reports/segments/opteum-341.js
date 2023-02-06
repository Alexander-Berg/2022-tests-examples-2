const DriverCard = require('../../../page/driverCard/DriverCard');
const ReportsSegments = require('../../../page/ReportsSegments');

describe('Фильтрация по "Отток водителей" с различными критериями', () => {

    const DATA = {
        days: {
            name: 'более 40 дней',
            index: 3,
        },
        statuses: [
            {
                name: 'Уволен',
                index: 3,
            },
            {
                name: 'Не работает',
                index: 1,
            },
        ],
        condition: {
            query: 'Yandex',
        },
    };

    let textsBeforeFilter;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it(`Выбрать в фильтре дней без заказов "${DATA.days.name}"`, () => {
        textsBeforeFilter = ReportsSegments.getCells({td: 2}).map(elem => elem.getText());

        ReportsSegments.daysFilter.input.click();
        ReportsSegments.selectOption[DATA.days.index].click();
    });

    it('Список водителей изменился', () => {
        expect(ReportsSegments.getCells({td: 2})).not.toHaveTextEqual(textsBeforeFilter);
    });

    it('В списке есть данные', () => {
        expect(ReportsSegments.getCells({td: 1})).toHaveTextOk();
    });

    DATA.statuses.forEach(({name, index}) => {

        it(`Выбрать в фильтре статуса "${name}"`, () => {
            ReportsSegments.statusFilter.input.click();
            ReportsSegments.selectOption[index].click();
        });

        it(`В списке отобразились водители со статусом "${name}"`, () => {
            expect(ReportsSegments.getCells({td: 1})).toHaveTextArrayEachEqual(name, {js: true});
        });

    });

    it(`Ввести в поиск по условиям работы "${DATA.condition.query}"`, () => {
        ReportsSegments.queryFilter(ReportsSegments.conditionsFilter, DATA.condition.query);
    });

    it(`В саджесте отобразились условия "${DATA.condition.query}"`, () => {
        expect(ReportsSegments.selectOption).toHaveTextArrayIncludes(DATA.condition.query);
    });

    it('Нажать на последние условие в саджесте', () => {
        ReportsSegments.selectOption.pop().click();
    });

    it('Список водителей изменился', () => {
        expect(ReportsSegments.getCells({td: 2})).not.toHaveTextEqual(textsBeforeFilter);
    });

    it('В списке есть данные', () => {
        expect(ReportsSegments.getCells({td: 1})).toHaveTextOk();
    });

    it('Открыть первого водителя из списка', () => {
        ReportsSegments.getCells({td: 1, tr: 1}).click();
    });

    it(`В карточке водителя отображается условие работы "${DATA.condition.query}"`, () => {
        ReportsSegments.switchTab();
        expect(DriverCard.selects.single).toHaveTextArrayIncludes(DATA.condition.query);
    });

});
