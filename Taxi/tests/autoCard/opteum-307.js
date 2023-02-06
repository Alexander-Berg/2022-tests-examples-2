const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

const servicesDropdownValues = [];
let variant;

describe('Выбор списка предоставляемых услуг', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль М025ММ и открыть его', () => {
        VehiclesPage.searchForAuto('М546АА99');
    });

    it('В разделе Услуги добавить "Кондиционер", "WiFi" и "Перевозка животных", если перечисленных услуг нет', () => {
        const defaultServicesDropdownValues = AutoCard.servicesBlock.dropdown.getText();

        if (!defaultServicesDropdownValues.match(/(Кондиционер|WiFi|Перевозка животных)/g)) {
            AutoCard.servicesBlock.dropdownSelect.click();
            AutoCard.servicesBlock.dropdownItems.wifi.click();
            servicesDropdownValues.push('WiFi');
            AutoCard.servicesBlock.dropdownItems.airConditioning.click();
            servicesDropdownValues.push('Кондиционер');
            AutoCard.servicesBlock.dropdownItems.animalsTransportation.click();
            servicesDropdownValues.push('Перевозна животных');
            AutoCard.servicesBlock.dropdownSelect.click();
            variant = 1;
        } else {
            AutoCard.servicesBlock.dropdownSelect.click();
            AutoCard.servicesBlock.dropdownClear.click();
            variant = 2;
        }
    });

    it('Сохранить изменения', () => {
        AutoCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        AutoCard.servicesBlock.dropdown.waitForDisplayed({timeout: 20_000});
    });

    it('Проверить значения после изменений', () => {
        const finalServicesDropdownValues = AutoCard.servicesBlock.dropdown.getText();

        if (variant === 1) {
            assert.isTrue(/(Кондиционер|WiFi|Перевозка животных)/g.test(finalServicesDropdownValues));
        }

        if (variant === 2) {
            assert.equal(finalServicesDropdownValues, '');
        }
    });
});
