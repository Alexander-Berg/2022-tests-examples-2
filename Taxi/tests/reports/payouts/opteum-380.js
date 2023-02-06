const ReportsPayouts = require('../../../page/ReportsPayouts');

describe('Выплаты. Фильтрация по статусу', () => {

    const DATA = {
        status: {
            default: 'Выплачено',
            abort: {
                title: 'Отмена',
                index: 3,
            },
        },
        filters: {
            default: [
                'Сформировано',
                'Отправлено в банк',
                'Выплачено',
            ],
        },
    };

    let length;

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo('?date_from=2021-02-21T16%3A35&date_to=2021-03-29T16%3A36');
    });

    it(`У всех выплат отображается статус "${DATA.status.default}"`, () => {
        expect(ReportsPayouts.getCells({td: 1})).toHaveTextArrayEachEqual(DATA.status.default);
        ({length} = ReportsPayouts.getCells({td: 1}));
    });

    it('В фильтре статусов по умолчанию выбраны корректные статусы', () => {
        expect(ReportsPayouts.filtersBlock.status.labels).toHaveTextEqual(DATA.filters.default);
    });

    DATA.filters.default.forEach(elem => {
        it(`Удалить фильтр "${elem}"`, () => {
            ReportsPayouts.filtersBlock.status.removes[0].click();
        });
    });

    it('Отобразилось больше выплат', () => {
        expect(ReportsPayouts.getCells({td: 1})).toHaveElemLengthAbove(length);
    });

    it(`Выбрать статус "${DATA.status.abort.title}"`, () => {
        ReportsPayouts.filtersBlock.status.select.click();
        ReportsPayouts.filtersBlock.status.options[DATA.status.abort.index].click();
    });

    it(`У всех выплат отображается статус "${DATA.status.abort.title}"`, () => {
        expect(ReportsPayouts.getCells({td: 1})).toHaveTextArrayEachEqual(DATA.status.abort.title);
    });

});
