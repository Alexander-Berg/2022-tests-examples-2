const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

describe('Указание позывного в авто', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    const plateNumber = 'K543MB085';

    it(`Найти в поиске автомобиль ${plateNumber} и открыть его`, () => {
        VehiclesPage.searchForAuto(`${plateNumber}`);
    });

    it('В разделе Параметры поменять Позывной на "Test"', () => {
        AutoCard.nickNameCell.click();
        AutoCard.clearWithBackspace(AutoCard.nickNameCell);
        AutoCard.type(AutoCard.nickNameCell, 'Test');
    });

    it('Сохранить изменения', () => {
        AutoCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        AutoCard.nickNameCell.waitForDisplayed({timeout: 5000});
    });

    it('Проверить значения после изменений', () => {
        assert.include(AutoCard.nickNameCell.getValue(), 'Test');
    });
});
