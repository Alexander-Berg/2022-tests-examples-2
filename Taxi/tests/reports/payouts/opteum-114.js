const DatePicker = require('../../../page/DatePicker');
const ReportsPayouts = require('../../../page/ReportsPayouts');

describe('Выплаты. Фильтрация списка по периоду', () => {

    const DATA = {
        placeholder: 'Пока ничего нет',
        payouts: {
            length: 6,
            status: 'Выплачено',
        },
    };

    it('Открыть страницу отчета по выплатам', () => {
        ReportsPayouts.goTo(
            '?date_from=2021-04-01T01%3A48&date_to=2021-04-01T01%3A48',
            {skipWait: true},
        );
    });

    it(`Отобразился плейсхолдер "${DATA.placeholder}"`, () => {
        expect(ReportsPayouts.reportTable.notFound).toHaveTextEqual(DATA.placeholder);
    });

    it('Выбрать предыдущий месяц из календаря', () => {
        DatePicker.open();
        DatePicker.pickPrevMonth();
    });

    it(`В таблице появилось "${DATA.payouts.length}" выплат`, () => {
        expect(ReportsPayouts.getCells({td: 1})).toHaveElemLengthEqual(DATA.payouts.length);
    });

    it(`У всех выплат статус "${DATA.payouts.status}"`, () => {
        expect(ReportsPayouts.getCells({td: 1})).toHaveTextArrayEachEqual(DATA.payouts.status);
    });

});
