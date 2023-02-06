const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

describe('Поиск авто по позывному, гос.номеру, СТС, VIN', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти автомобиль по позывному', () => {
        VehiclesPage.type(VehiclesPage.searchField, 'K555KK10');
        browser.pause(2000);
        assert.isAtLeast(VehiclesPage.nickNameCell.length, 1);
    });

    it('Найти автомобиль по гос.номеру', () => {
        VehiclesPage.clearWithBackspace(VehiclesPage.searchField);
        VehiclesPage.type(VehiclesPage.searchField, 'К555КК10');
        browser.pause(2000);
        assert.equal(VehiclesPage.vehiclePlateCell.getText(), 'К555КК10');
    });

    it('Найти автомобиль по СТС', () => {
        VehiclesPage.clearWithBackspace(VehiclesPage.searchField);
        VehiclesPage.type(VehiclesPage.searchField, 'TYP123456789TYP12');
        browser.pause(2000);
        assert.equal(VehiclesPage.stsCell.getText(), 'TYP123456789TYP12');
    });
});
