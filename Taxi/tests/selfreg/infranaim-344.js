const { assert } = require('chai');
const citizenshipPage = require('../../pageobjects/selfreg/page.selfreg.citizenship');
const vehiclePage = require('../../pageobjects/selfreg/page.selfreg.vehicle-type');

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /vehicle-type (пешком)', () => {
    it('пройти до страницы /vehicle-type', () => {
        vehiclePage.open();
    });

    it('выбрать Пешего курьера', () => {
        vehiclePage.selectCourierType('foot');
        assert.equal(vehiclePage.btnRdActive.getText(), 'Пешком', 'Тип курьера отличается от Пешком');
    });

    it('нажать Далее', () => {
        vehiclePage.btnNext.click();
        citizenshipPage.drpdwnCitizenship.waitForDisplayed();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/citizenship');
    });
});
