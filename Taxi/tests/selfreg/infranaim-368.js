const { assert } = require('chai');
const edaPage = require('../../pageobjects/selfreg/page.selfreg.service-eda');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /personal-data (все поля)', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить форму', () => {
        personalPage.fillForm();
    });

    it('форма содержит правильные данные', () => {
        assert.equal(personalPage.fldDateBirth.getValue(), '11.09.2000');
        assert.equal(personalPage.fldFirstName.getValue(), 'Марк');
        assert.equal(personalPage.fldSecondName.getValue(), 'Кастромской');
        assert.equal(personalPage.fldThirdName.getValue(), 'Кастянович');
        assert.equal(personalPage.fldContactEmail.getValue(), 'dsa@wqe.zxc');
        assert.equal(personalPage.fldTelegram.getValue(), 'vasya');
    });

    it('нажать кнопку Далее', () => {
        personalPage.goNext();
        edaPage.txtHeaderEda.waitForDisplayed();
        // eslint-disable-next-line no-undef
        assert.equal(browser.getUrl(), 'https://courier-selfreg.eda.tst.yandex.net/service-eda');
    });
});
