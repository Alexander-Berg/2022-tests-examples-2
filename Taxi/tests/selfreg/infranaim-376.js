const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Негатив кнопки "Дальше" страницы personal data без e-mail', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить поля', () => {
        personalPage.fillForm();
    });

    it('очистить поле e-mail', () => {
        personalPage.fldContactEmail.click();
        personalPage.clearWithBackspace(personalPage.fldContactEmail);
    });

    it('нажать кнопку далее', () => {
        personalPage.goNext();
        assert.isTrue(personalPage.hint.isDisplayed());
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/personal-data');
    });
});
