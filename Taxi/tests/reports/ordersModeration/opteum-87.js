const DatePicker = require('../../../page/DatePicker');
const ReportsOrdersModeration = require('../../../page/ReportsOrdersModeration');

describe('Фильтрация: по периоду', () => {

    const DATA = {
        date: '1 февр. 2022 г., 15:35 – 31 мар. 2022 г., 15:35',
    };

    it('Открыть страницу модерации заказов', () => {
        ReportsOrdersModeration.goTo('?from=2022-02-01T15%3A35&to=2022-03-31T15%3A35');
    });

    it('В фильтре даты отображается корректный период', () => {
        expect(DatePicker.block.filter).toHaveAttributeEqual('value', DATA.date);
    });

    it('Открыть фильтр дат', () => {
        DatePicker.open();
    });

    it('Выбрать период с начала предыдущего месяца', () => {
        DatePicker.pickFromPrevMonthStartToToday();
    });

    it('Отображается список с заявками', () => {
        expect(ReportsOrdersModeration.getCells({td: 1})).toHaveElemLengthAbove(0);
    });

});
