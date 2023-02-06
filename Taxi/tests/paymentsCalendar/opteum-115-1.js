const PaymentsCalendar = require('../../page/PaymentsCalendar');

describe('Проверка фильтров в календаре списаний: поиск', () => {

    const DATA = {
        query: 'В070ВС070',
        result: 'В 070 ВС 070',
    };

    it('Открыть страницу Календарь списаний', () => {
        PaymentsCalendar.goTo();
    });

    it(`В поле Поиск вводим "${DATA.query}"`, () => {
        PaymentsCalendar.infoBlockClose.waitForDisplayed();
        PaymentsCalendar.infoBlockClose.click();
        PaymentsCalendar.searchField.setValue(DATA.query);
    });

    it(`В таблице отобразилась машина "${DATA.result}"`, () => {
        expect(PaymentsCalendar.firstVehiclePlateNumberCell).toHaveTextStartsWith(DATA.result);
    });

});
