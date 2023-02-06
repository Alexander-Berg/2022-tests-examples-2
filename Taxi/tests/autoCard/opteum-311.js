const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

const tariffsDropdownValues = [];
let variant;

describe('Настройка тарифа "От борта"', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль Т681СС491 и открыть его', () => {
        VehiclesPage.searchForAuto('Т681СС491');
    });

    it('Настройка тарифа "От борта"', () => {
        const defaultTariffsDropdownValues = AutoCard.tariffsBlock.dropdown.getText();

        if (!defaultTariffsDropdownValues.match(/(Эконом|Комфорт)/g)) {
            AutoCard.tariffsBlock.dropdownSelect.click();
            AutoCard.tariffsBlock.dropdownItems.economy.click();
            tariffsDropdownValues.push('Эконом');
            AutoCard.tariffsBlock.dropdownItems.comfort.click();
            tariffsDropdownValues.push('Комфорт');
            AutoCard.tariffsBlock.dropdownSelect.click();
            variant = 1;
        } else {
            AutoCard.tariffsBlock.dropdownSelect.click();
            AutoCard.tariffsBlock.dropdownClear.click();
            variant = 2;
        }
    });

    it('Сохранить изменения', () => {
        AutoCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        AutoCard.tariffsBlock.dropdownControl.waitForDisplayed({timeout: 30_000});
    });

    it('Проверить значения после изменений', () => {
        const finalTariffsDropdownValues = AutoCard.tariffsBlock.dropdown.getText();

        if (variant === 1) {
            assert.isTrue(/(Эконом|Комфорт)/g.test(finalTariffsDropdownValues));
        }

        if (variant === 2) {
            assert.equal(finalTariffsDropdownValues, '');
        }
    });
});
