const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

const categoriesDropdownValues = [];
let variant;

describe('Выбор поддерживаемых категорий', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль Y724HP324 и открыть его', () => {
        VehiclesPage.searchForAuto('У724НР324');
    });

    it('В разделе категории добавить "Эконом", "Комфорт", "Стандарт", "Бизнес" и "Универсальный", если перечисленных категорий нет', () => {
        const defaultCategoriesDropdownValues = AutoCard.categoriesBlock.dropdown.getText();

        if (!defaultCategoriesDropdownValues.match(/(Эконом|Комфорт|Стандарт|Бизнес|Универсальный)/g)) {
            AutoCard.categoriesBlock.dropdownSelect.click();
            AutoCard.categoriesBlock.dropdownItems.economy.click();
            categoriesDropdownValues.push('Эконом');
            AutoCard.categoriesBlock.dropdownItems.comfort.click();
            categoriesDropdownValues.push('Комфорт');
            AutoCard.categoriesBlock.dropdownItems.standard.click();
            categoriesDropdownValues.push('Стандарт');
            AutoCard.categoriesBlock.dropdownItems.business.click();
            categoriesDropdownValues.push('Универсальный');
            AutoCard.categoriesBlock.dropdownSelect.click();
            variant = 1;
        } else {
            AutoCard.categoriesBlock.dropdownSelect.click();
            AutoCard.categoriesBlock.dropdownClear.click();
            variant = 2;
        }
    });

    it('Сохранить изменения', () => {
        AutoCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        AutoCard.categoriesBlock.dropdown.waitForDisplayed({timeout: 20_000});
    });

    it('Проверить значения после изменений', () => {
        const finalCategoriesDropdownValues = AutoCard.categoriesBlock.dropdown.getText();

        if (variant === 1) {
            assert.isTrue(/(Эконом|Комфорт|Стандарт|Бизнес|Универсальный)/g.test(finalCategoriesDropdownValues));
        }

        if (variant === 2) {
            assert.equal(finalCategoriesDropdownValues, '');
        }
    });
});
