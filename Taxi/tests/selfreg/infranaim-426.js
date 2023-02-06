const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage();

describe('Негативные проверки поля "Фамилия" страницы /personal-data', () => {
    it('открыть страницу /personal-data', () => {
        personalPage.open();
    });

    const secondName = '123';
    it(`ввести ${secondName} в поле Фамилия`, () => {
        personalPage.fillSecondName(secondName);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Фамилия первый раз', () => {
        personalPage.clearWithBackspace(personalPage.fldSecondName);
    });

    const anotherSecondName = '!"№:,.;';
    it(`ввести ${anotherSecondName} в поле Фамилия`, () => {
        personalPage.fillSecondName(anotherSecondName);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Фамилия второй раз', () => {
        personalPage.clearWithBackspace(personalPage.fldSecondName);
    });

    const spaceChar = ' ';
    it(`ввести ${spaceChar} в поле Фамилия`, () => {
        personalPage.fillSecondName(spaceChar);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Фамилия третий раз', () => {
        personalPage.clearWithBackspace(personalPage.fldSecondName);
    });

    const yetAnotherSecondName = 'asdasd';
    it(`ввести ${yetAnotherSecondName} в поле Фамилия`, () => {
        personalPage.fillSecondName(yetAnotherSecondName);
        personalPage.hint.waitForDisplayed();
    });
});
