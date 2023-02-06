const moment = require('moment');
const re = require('../../../../../utils/consts/re');
const ReportsSegments = require('../../../page/ReportsSegments');

moment.locale('ru');

const getDatesEpoch = td => ReportsSegments
    .getCells({td})
    .map(elem => moment(elem.getText(), 'D MMM YYYY').valueOf());

describe('Сортировка в таблице сегменты водителей', () => {

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Отображаются даты последнего заказа', () => {
        expect(ReportsSegments.getCells({td: 4})).toHaveTextMatch(re.dates.one);
    });

    it('Нажать на сортировку дат последнего заказа', () => {
        ReportsSegments.reportTable.header.sort[0].click();
    });

    it('Даты последнего заказа отсортировались по убыванию', () => {
        const dates = getDatesEpoch(4);
        expect(dates).toEqual(dates.sort((a, b) => a - b));
    });

    it('Нажать на сортировку дат последнего заказа ещё раз', () => {
        ReportsSegments.reportTable.header.sort[0].click();
    });

    it('Даты последнего заказа отсортировались по возрастанию', () => {
        const dates = getDatesEpoch(4);
        expect(dates).toEqual(dates.sort((a, b) => b - a));
    });

    it('Отображаются даты принятия', () => {
        expect(ReportsSegments.getCells({td: 5})).toHaveTextMatch(re.dates.one);
    });

    it('Нажать на сортировку дат принятия', () => {
        ReportsSegments.reportTable.header.sort[1].click();
    });

    it('Даты принятия отсортировались по убыванию', () => {
        const dates = getDatesEpoch(5);
        expect(dates).toEqual(dates.sort((a, b) => a - b));
    });

    it('Нажать на сортировку дат принятия ещё раз', () => {
        ReportsSegments.reportTable.header.sort[1].click();
    });

    it('Даты принятия отсортировались по возрастанию', () => {
        const dates = getDatesEpoch(5);
        expect(dates).toEqual(dates.sort((a, b) => b - a));
    });

});
