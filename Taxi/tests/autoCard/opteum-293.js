const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');

describe('Создание записи нового авто', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('На странице Автомобилей нажать на плюс', () => {
        VehiclesPage.addVehicleButton.waitForDisplayed({timeout: 1000});
        VehiclesPage.addVehicleButton.click();
    });

    it('Выбрать в подразделе Услуги "WiFi" и "Кондиционер"', () => {
        AutoCard.servicesBlock.dropdownSelect.click();
        AutoCard.servicesBlock.dropdownItems.wifi.click();
        AutoCard.servicesBlock.dropdownSelect.click();
        AutoCard.servicesBlock.dropdownSelect.click();
        AutoCard.servicesBlock.dropdownItems.airConditioning.click();
        AutoCard.servicesBlock.dropdownSelect.click();
    });

    it('Выбрать в подразделе Категории "Комфорт", "Эконом"', () => {
        AutoCard.categoriesBlock.dropdownSelect.click();
        AutoCard.categoriesBlock.dropdownItems.comfort.click();
        AutoCard.categoriesBlock.dropdownSelect.click();
        AutoCard.categoriesBlock.dropdownSelect.click();
        AutoCard.categoriesBlock.dropdownItems.economy.click();
        AutoCard.categoriesBlock.dropdownSelect.click();
    });

    it('Заполнить подраздел Детали валидными данными и сохранить авто', () => {
        AutoCard.fillRequiredData();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        AutoCard.servicesBlock.dropdown.waitForDisplayed({timeout: 20_000});
    });

    it('Проверить новые данные', () => {
        expect(AutoCard.servicesBlock.dropdown).toHaveTextIncludes('WiFi');
        expect(AutoCard.servicesBlock.dropdown).toHaveTextIncludes('Кондиционер');

        expect(AutoCard.categoriesBlock.dropdown).toHaveTextIncludes('Комфорт');
        expect(AutoCard.categoriesBlock.dropdown).toHaveTextIncludes('Эконом');
    });
});
