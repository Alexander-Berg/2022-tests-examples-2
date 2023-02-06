const { assert } = require('chai');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /placement ', () => {
    it('пройти до страницы /vehicle', () => {
        vehiclePage.open();
    });

    it('отображается правильный урл', () => {
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/vehicle-type');
    });
});
