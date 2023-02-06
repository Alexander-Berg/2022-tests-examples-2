const { assert } = require('chai');
const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');
const placementPage = require('../../pageobjects/selfreg/page.selfreg.placement');

describe('Действие по нажатию кнопки "Дальше" /phone', () => {
    it('подтверждаем номер телефона с помощью смс-кода', () => {
        phonePage.open();
        phonePage.fillPhoneNumber();
        phonePage.confirmCode();
    });

    it('нажать кнопку "Дальше"', () => {
        phonePage.btnNext.click();
        placementPage.btnNext.waitForDisplayed();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/placement');
    });
});
