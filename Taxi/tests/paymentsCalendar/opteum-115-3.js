const AutoCard = require('../../page/AutoCard');
const PaymentsCalendar = require('../../page/PaymentsCalendar');

describe('Проверка фильтров в календаре списаний: категория', () => {

    const DATA = {
        category: 'Курьер',
    };

    it('Открыть страницу Календарь списаний', () => {
        PaymentsCalendar.goTo();
    });

    it(`В фильтре Категории выбираем категорию "${DATA.category}"`, () => {
        PaymentsCalendar.filtersBlock.categories.click();
        PaymentsCalendar.filtersBlock.categoriesItems.food.click();
    });

    it('Открыть первую машину', () => {
        browser.pause(3000);
        PaymentsCalendar.firstVehicleStatusCell.click();
    });

    it(`В блоке категорий отображается "${DATA.category}"`, () => {
        expect(AutoCard.categoriesBlock.dropdown).toHaveTextIncludes(DATA.category);
    });

});
