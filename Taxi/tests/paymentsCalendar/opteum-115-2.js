const PaymentsCalendar = require('../../page/PaymentsCalendar');

describe('Проверка фильтров в календаре списаний: статус', () => {

    const DATA = {
        status: 'В угоне',
    };

    it('Открыть страницу Календарь списаний', () => {
        PaymentsCalendar.goTo();
    });

    it(`В фильтре Статусы выбираем статус "${DATA.status}"`, () => {
        PaymentsCalendar.filtersBlock.statuses.click();
        PaymentsCalendar.filtersBlock.statusesItems.stolen.click();
    });

    it(`Отобразилась машина со статусом "${DATA.status}"`, () => {
        expect(PaymentsCalendar.firstVehicleStatusCell).toHaveTextEqual(DATA.status);
    });

});
