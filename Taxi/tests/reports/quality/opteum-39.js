const AutoCard = require('../../../page/AutoCard');
const ReportsQuality = require('../../../page/ReportsQuality');
const {assert} = require('chai');

let driversCount;

describe('Фильтр: указание категории', () => {

    it('Открыть страницу Качество', () => {
        ReportsQuality.goTo();
    });

    it('Запомнить количество водителей без фильтра Категорий', () => {
        driversCount = ReportsQuality.driversCount.getText();
    });

    it('В фильтре "Категории" выбрать "Комфорт"', () => {
        ReportsQuality.filtersBlock.categories.dropdown.click();
        ReportsQuality.filtersBlock.categories.comfort.click();
        ReportsQuality.resultTable.firstNickName.click();
        assert.include(AutoCard.categoriesBlock.dropdown.getText(), 'Комфорт');
    });

    it('Не отчищая фильтр, выбрать "Грузовой" и "Стандарт" и открыть первое авто', () => {
        browser.back();
        ReportsQuality.filtersBlock.categories.dropdown.waitForDisplayed();
        ReportsQuality.filtersBlock.categories.select.click();
        ReportsQuality.filtersBlock.categories.econom.click();
        ReportsQuality.filtersBlock.categories.corporate.click();
        ReportsQuality.filtersBlock.categories.select.click();
        ReportsQuality.resultTable.firstNickName.click();
    });

    it('Сверить информацию в карточке авто с фильтром', () => {
        assert.include(AutoCard.categoriesBlock.dropdown.getText(), 'Комфорт');
        assert.include(AutoCard.categoriesBlock.dropdown.getText(), 'Эконом');
        assert.include(AutoCard.categoriesBlock.dropdown.getText(), 'Корпоративный');
    });

    it('Сбросить фильтр Категорий', () => {
        browser.back();
        ReportsQuality.filtersBlock.categories.clear.click();
    });

    it('Проверить количество водителей', () => {
        assert.equal(ReportsQuality.driversCount.getText(), driversCount);
    });

});
