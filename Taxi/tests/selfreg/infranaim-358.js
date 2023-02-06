const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Позитивные проверки поля "Фамилия" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    const name = 'Петр';
    it(`ввести ${name} в Фамилию`, () => {
        personalPage.fldSecondName.setValue(name);
        personalPage.selectFirstDropdownItem();
        assert.match(personalPage.fldSecondName.getValue(), /Петр[а-я]*/);
    });

    it('очистить поле', () => {
        personalPage.clearWithBackspace(personalPage.fldSecondName);
    });

    const anotherName = 'Иван';
    it(`ввести ${anotherName} в поле Фамилию`, () => {
        personalPage.fldSecondName.setValue(anotherName);
        personalPage.selectFirstDropdownItem();
        assert.match(personalPage.fldSecondName.getValue(), /Иван[а-я]*/);
    });
});
