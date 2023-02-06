const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

describe('Редактирование записи существующего авто', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль 11111111111111111, открыть', () => {
        VehiclesPage.searchField.setValue('11111111111111111');
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.statusDropdownItems.works.click();
        VehiclesPage.statusesDropdown.click();
        VehiclesPage.vehiclePlateCell.waitForDisplayed();
        VehiclesPage.vehiclePlateCell.click();
        AutoCard.backButton.waitForDisplayed();
    });

    it('Поменять статус на "Не работает" и сохранить', () => {
        AutoCard.statusBlock.dropdownSelect.click();
        AutoCard.statusBlock.dropdownItems.doesntWork.click();
        AutoCard.saveButton.click();
        browser.refresh();
        assert.include(AutoCard.statusBlock.dropdown.getText(), 'Не работает');
    });

    it('Поменять комплектацию на автоматическую и сохранить', () => {
        AutoCard.kppBlock.dropdownSelect.click();
        AutoCard.kppBlock.dropdownItems.automatic.click();
        AutoCard.saveButton.click();
        browser.refresh();
        assert.include(AutoCard.kppBlock.dropdown.getText(), 'Автомат');
    });
});
