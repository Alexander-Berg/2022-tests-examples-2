const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Негативные проверки поля "Логин в Telegram" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    const inputs = ['1234', '@sdddd', 'sdddd', ':№%:№:№:'];
    inputs.forEach(text => {
        it(`ввести в поле логина ${text}`, () => {
            personalPage.fillTelegrm(text);
            personalPage.hint.waitForDisplayed();
            assert.equal(personalPage.hint.getText(), 'Некоррректный логин');
        });

        it('очистить поле Telegram', () => {
            personalPage.clearWithBackspace(personalPage.fldTelegram);
        });
    });
});
