const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Позитивные проверки поля "Имя" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    const name = 'Петр';
    it(`ввести ${name} в поле имя`, () => {
        personalPage.fldFirstName.setValue(name);
        personalPage.selectFirstDropdownItem();
        assert.match(personalPage.fldFirstName.getValue(), /Петр[а-я]*/);
    });

    it('очистить поле', () => {
        personalPage.clearWithBackspace(personalPage.fldFirstName);
    });

    const anotherName = 'Иван';
    it(`ввести ${anotherName} в поле имя`, () => {
        personalPage.fldFirstName.setValue(anotherName);
        personalPage.selectFirstDropdownItem();
        assert.match(personalPage.fldFirstName.getValue(), /Иван[а-я]*/);
    });
});
