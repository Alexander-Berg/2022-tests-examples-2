const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');

describe('Фильтрация списка авто по статусам, категориям, услугам', () => {

    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('В фильтре Статус выбрать "Работает"', () => {
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.statusDropdownItems.works.click();
        VehiclesPage.statusesDropdown.click();

        expect(VehiclesPage.allStatuses).toHaveTextArrayEachEqual('Работает');
    });

    it('В фильтре Статус выбрать "Не работает"', () => {
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.statusDropdownItems.doesntWork.click();
        VehiclesPage.statusesDropdown.click();

        expect(VehiclesPage.allStatuses).toHaveTextArrayEachEqual('Не работает');
    });

    it('В фильтре Статус выбрать "В гараже"', () => {
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.statusDropdownItems.inGarage.click();
        VehiclesPage.statusesDropdown.click();

        expect(VehiclesPage.allStatuses).toHaveTextArrayEachEqual('В гараже');
    });

    it('В фильтре Категории выбрать "VIP"', () => {
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.categoriesDropdown.click();
        VehiclesPage.categoriesDropdownItems.vip.click();
        VehiclesPage.categoriesDropdown.click();

        VehiclesPage.getCells({tr: 1, td: 6}).click();
        expect(AutoCard.getAutoCategories).toHaveTextArrayIncludes('VIP');
    });

    it('В фильтре Категории выбрать "Эконом"', () => {
        AutoCard.backButton.click();
        VehiclesPage.categoriesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.categoriesDropdown.click();
        VehiclesPage.categoriesDropdownItems.economy.click();
        VehiclesPage.categoriesDropdown.click();

        VehiclesPage.getCells({tr: 1, td: 6}).click();
        expect(AutoCard.getAutoCategories).toHaveTextArrayIncludes('Эконом');
    });

    it('В фильтре Категории выбрать "Комфорт"', () => {
        AutoCard.backButton.click();
        VehiclesPage.categoriesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.categoriesDropdown.click();
        VehiclesPage.categoriesDropdownItems.comfort.click();
        VehiclesPage.categoriesDropdown.click();

        VehiclesPage.getCells({tr: 1, td: 6}).click();
        expect(AutoCard.getAutoCategories).toHaveTextArrayIncludes('Комфорт');
    });

    it('В фильтре Услуги выбрать "WiFi"', () => {
        AutoCard.backButton.click();
        VehiclesPage.categoriesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.servicesDropdown.click();
        VehiclesPage.servicesDropdownItems.wifi.click();
        VehiclesPage.servicesDropdown.click();

        VehiclesPage.getCells({tr: 1, td: 6}).click();
        expect(AutoCard.getAutoServices).toHaveTextArrayIncludes('WiFi');
    });

    it('В фильтре Услуги выбрать "Кондиционер"', () => {
        AutoCard.backButton.click();
        VehiclesPage.servicesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.servicesDropdown.click();
        VehiclesPage.servicesDropdownItems.airConditioning.click();
        VehiclesPage.servicesDropdown.click();

        VehiclesPage.getCells({tr: 1, td: 6}).click();
        expect(AutoCard.getAutoServices).toHaveTextArrayIncludes('Кондиционер');
    });

    it('В фильтре Услуги выбрать "Перевозка животных"', () => {
        AutoCard.backButton.click();
        VehiclesPage.servicesDropdown.click();
        VehiclesPage.clearFilter.click();
        VehiclesPage.servicesDropdown.click();
        VehiclesPage.servicesDropdownItems.animalsTransportation.click();
        VehiclesPage.servicesDropdown.click();

        VehiclesPage.getCells({tr: 1, td: 6}).click();
        expect(AutoCard.getAutoServices).toHaveTextArrayIncludes('Перевозка животных');
    });
});
