const LegalEntitiesPage = require('../page/LegalEntitiesPage');
const {assert} = require('chai');

describe('Просмотр существующего перевозчика', () => {
    it('Открыть страницу перевозчиков ', () => {
        LegalEntitiesPage.goTo();
    });

    it('Найти перевозчика', () => {
        LegalEntitiesPage.type(LegalEntitiesPage.searchField, 'Vasya');
        browser.pause(2000);
        assert.equal(LegalEntitiesPage.allEntities.length, 1);
        assert.equal(LegalEntitiesPage.ogrnCell.getText(), '100');
    });

    it('Открыть найденного перевозчика', () => {
        LegalEntitiesPage.nameLegalEntity.click();
        browser.pause(2000);
        assert.equal(LegalEntitiesPage.ogrnField.getValue(), '100');
        assert.equal(LegalEntitiesPage.nameField.getValue(), 'Vasya');
        assert.equal(LegalEntitiesPage.addressField.getValue(), 'Street');
    });

    it('Закрыть окно найденного перевозчика', () => {
        LegalEntitiesPage.closeLegalEntity.click();
        assert.equal(LegalEntitiesPage.saveLegalEntity.isDisplayed(), false);
    });
});
