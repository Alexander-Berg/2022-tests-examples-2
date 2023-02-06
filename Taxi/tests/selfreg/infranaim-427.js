const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Негативные проверки поля "Имя" страницы /personal-data', () => {
    it('открыть страницу /personal-data', () => {
        personalPage.open();
    });

    const name = '123';
    it(`ввести ${name} в поле Имя`, () => {
        personalPage.fillFirstName(name);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Фамилия', () => {
        personalPage.clearWithBackspace(personalPage.fldFirstName);
    });

    const anotherName = '!"№:,.;';
    it(`ввести ${anotherName} в поле Имя`, () => {
        personalPage.fillFirstName(anotherName);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Имя', () => {
        personalPage.clearWithBackspace(personalPage.fldFirstName);
    });

    const spaceChar = ' ';
    it(`ввести ${spaceChar} в поле Имя`, () => {
        personalPage.fillFirstName(spaceChar);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Фамилия второй раз', () => {
        personalPage.clearWithBackspace(personalPage.fldFirstName);
    });

    const yetAnotherName = 'asdasd';
    it(`ввести ${yetAnotherName} в поле Имя`, () => {
        personalPage.fillFirstName(yetAnotherName);
        personalPage.hint.waitForDisplayed();
    });
});
