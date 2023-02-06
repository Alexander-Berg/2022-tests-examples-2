const ReportsSegments = require('../../../page/ReportsSegments');

describe('Фильтр: указание сегмента', () => {

    const DATA = {
        dropdowns: [
            {
                name: 'Отток водителей',
                index: 0,
            },
            {
                name: 'Без заказов',
                index: 1,
            },
        ],
    };

    const defaultName = DATA.dropdowns[0].name;

    let textsBeforeFilter;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it(`Отображается фильтр сегментов водителей "${defaultName}"`, () => {
        expect(ReportsSegments.segmentsFilter.input).toHaveTextEqual(defaultName);
    });

    DATA.dropdowns.reverse().forEach(({name, index}) => {

        it(`Выбрать в фильтре сегментов "${name}"`, () => {
            textsBeforeFilter = ReportsSegments.getCells({td: 2}).map(elem => elem.getText());

            ReportsSegments.segmentsFilter.input.click();
            ReportsSegments.selectOption[index].click();
        });

        it('Список водителей изменился', () => {
            expect(ReportsSegments.getCells({td: 2})).not.toHaveTextEqual(textsBeforeFilter);
        });

        it('В списке есть данные', () => {
            expect(ReportsSegments.getCells({td: 1})).toHaveTextOk();
        });

        it(`Отображается выбранный фильтр сегментов водителей "${name}"`, () => {
            expect(ReportsSegments.segmentsFilter.input).toHaveTextEqual(name);
        });

    });

});
