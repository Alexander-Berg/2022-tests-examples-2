const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Позитивные проверки поля "Отчество" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    const name = 'Петр';
    it(`ввести ${name} в Отчество`, () => {
        personalPage.fldThirdName.setValue(name);
        personalPage.selectFirstDropdownItem();
        assert.match(personalPage.fldThirdName.getValue(), /^Петр[а-я]*/);
    });

    it('очистить поле', () => {
        personalPage.clearWithBackspace(personalPage.fldThirdName);
    });

    const anotherName = 'Иван';
    it(`ввести ${anotherName} в Отчество`, () => {
        personalPage.fldThirdName.setValue(anotherName);
        personalPage.selectFirstDropdownItem();
        assert.match(personalPage.fldThirdName.getValue(), /^Иван[а-я]*/);
    });
});
