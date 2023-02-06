const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Негативные проверки поля "Отчество" страницы /personal-data', () => {
    it('открыть страницу /personal-data', () => {
        personalPage.open();
    });

    const thirdName = '123';
    it(`ввести ${thirdName} в поле Отчество`, () => {
        personalPage.fillThirdName(thirdName);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Отчество', () => {
        personalPage.clearWithBackspace(personalPage.fldThirdName);
    });

    const symbols = '!"№:,.;';
    it(`ввести ${symbols} в поле Отчество`, () => {
        personalPage.fillThirdName(symbols);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Отчество второй раз', () => {
        personalPage.clearWithBackspace(personalPage.fldThirdName);
    });

    const spaceChar = ' ';
    it(`ввести ${spaceChar} в поле Отчество`, () => {
        personalPage.fillThirdName(spaceChar);
        personalPage.hint.waitForDisplayed();
    });

    it('очистить поле Отчество третий раз', () => {
        personalPage.clearWithBackspace(personalPage.fldThirdName);
    });

    const engName = 'asdasd';
    it(`ввести ${engName} в поле Отчество`, () => {
        personalPage.fillThirdName(engName);
        personalPage.hint.waitForDisplayed();
    });
});
