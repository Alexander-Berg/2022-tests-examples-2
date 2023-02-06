const ReportsSegments = require('../../../page/ReportsSegments');

describe('Фильтр: указание статуса водителя', () => {

    const DATA = {
        default: 'Все статусы',
        dropdown: {
            name: 'Уволен',
            index: 3,
        },
    };

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo(
            '?segment_id=churn_rate'
          + '&churn_rate_id=over_40',
        );
    });

    it('Отображается фильтр статусов', () => {
        expect(ReportsSegments.statusFilter.input).toHaveTextEqual(DATA.default);
    });

    it(`Выбрать в фильтре статуса "${DATA.dropdown.name}"`, () => {
        ReportsSegments.statusFilter.input.click();
        ReportsSegments.selectOption[DATA.dropdown.index].click();
    });

    it(`В списке отобразились водители со статусом "${DATA.dropdown.name}"`, () => {
        expect(ReportsSegments.getCells({td: 1})).toHaveTextArrayEachEqual(DATA.dropdown.name);
    });

});
