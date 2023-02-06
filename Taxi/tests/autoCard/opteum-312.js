const AutoCard = require('../../page/AutoCard');
const VehiclesPage = require('../../page/VehiclesPage');
const {assert} = require('chai');

describe('Просмотр информации к какому водителю присоединена машина"', () => {
    it('Открыть страницу автомобилей', () => {
        VehiclesPage.goTo();
    });

    it('Найти в поиске автомобиль Х941ОС531 и открыть его', () => {
        VehiclesPage.searchForAuto('Х941ОС531');
    });

    it('Перейти в табу водители', () => {
        AutoCard.tabDrivers.click();
        AutoCard.driversList.waitForDisplayed({timeout: 3000});
    });

    it('Проверить привязанного водителя к авто', () => {
        assert.isTrue(AutoCard.firstDriverName.isDisplayed());
    });
});
