const AutoCard = require('../../page/AutoCard');
const PaymentsCalendar = require('../../page/PaymentsCalendar');

describe('Проверка фильтров в календаре списаний: услуги и чекбокс', () => {

    const DATA = {
        service: 'Кондиционер',
        check: /^(Нет|Не выбрано)$/,
    };

    it('Открыть страницу Календарь списаний', () => {
        PaymentsCalendar.goTo();
    });

    it(`В фильтре Услуг выбираем "${DATA.service}"`, () => {
        PaymentsCalendar.filtersBlock.services.click();
        PaymentsCalendar.filtersBlock.servicesItems.airConditioning.click();
    });

    it('Открыть первую машину', () => {
        browser.pause(3000);
        PaymentsCalendar.firstVehicleStatusCell.click();
    });

    it(`В блоке услуг отображается "${DATA.service}"`, () => {
        expect(AutoCard.servicesBlock.dropdown).toHaveTextIncludes(DATA.service);
    });

    it('Очистить фильтр услуг', () => {
        browser.back();
        PaymentsCalendar.filtersBlock.services.click();
        PaymentsCalendar.filtersBlock.servicesClear.click();
        PaymentsCalendar.vehiclesTable.waitForDisplayed();
    });

    it('Снимаем чекбокс Только арендные', () => {
        if (PaymentsCalendar.filtersBlock.onlyRentCheckbox.isSelected()) {
            PaymentsCalendar.filtersBlock.onlyRentCheckbox.click();
        }
    });

    it('Открыть первую машину', () => {
        browser.pause(3000);
        PaymentsCalendar.firstVehicleStatusCell.click();
    });

    it(`В блоке машин отображается "${DATA.check}"`, () => {
        expect(AutoCard.parkCarDropdown).toHaveTextMatch(DATA.check);
    });

});
