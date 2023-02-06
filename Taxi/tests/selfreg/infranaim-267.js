const { assert } = require('chai');
const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Негативные проверки поля "E-mail" страницы /personal-data', () => {
    it('открыть страницу /personal-data', () => {
        personalPage.open();
    });

    const inputs = ['1234', 'asdasd', '!#!@#!', 'asd@', 'asd@asd', 'asd@asd.', 'asd@asd.r', 'asd@asd.ru.', 'asd@asd.ru.r', 'asd@asd@ru', 'лол@кек.рф'];
    inputs.forEach(text => {
        it(`ввести ${text} в поле E-mail`, () => {
            personalPage.fillContactEmail(text);
            personalPage.hint.waitForDisplayed();
            assert.equal(personalPage.hint.getText(), 'Некорректная почта');
        });

        it('очистить поле E-mail', () => {
            personalPage.clearWithBackspace(personalPage.fldContactEmail);
        });
    });
});
