const { assert } = require('chai');
const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();
const placementPage = new dict.placementPage();

describe('Действие по нажатию кнопки "Дальше" /phone', () => {
    it('подтверждаем номер телефона с помощью смс-кода', () => {
        phonePage.open();
        phonePage.fillPhoneNumber();
        phonePage.btnGetCode.click();
        phonePage.confirmCode();
    });

    it('нажать кнопку "Дальше"', () => {
        phonePage.btnNext.click();
        placementPage.btnNext.waitForDisplayed();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/placement');
    });
});
