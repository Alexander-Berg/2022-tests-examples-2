const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Позитивные проверки поля "Дата рождения" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('В поле "Дата рождения" вводим "01.01.2000" ', () => {
        personalPage.fillDateBirth('01.01.2000');
        assert.isFalse(personalPage.itemErrorDescription.isExisting());
    });

    it('Стираем предыдущее значение и в поле "Дата рождения" вводим значение "01.01.1980"" ', () => {
        personalPage.clearWithBackspace(personalPage.fldDateBirth);
        personalPage.fillDateBirth('01.01.1980');
        assert.isFalse(personalPage.itemErrorDescription.isExisting());
    });
});
