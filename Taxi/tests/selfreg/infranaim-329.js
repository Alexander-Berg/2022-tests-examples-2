const { assert } = require('chai');
const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');

describe('Негативные проверки поля "кода из смс"', () => {
    it('пройти до страницы /phone', () => {
        phonePage.open();
    });

    it('В поле "Код из смс" вводим код "ывфывф"', () => {
        phonePage.fillCode('ывфывф');
        phonePage.hintError.waitForDisplayed();
        phonePage.btnNext.waitForClickable({ reverse: true });
    });

    it('Очищаем поле для кода', () => {
        phonePage.clearWithBackspace(phonePage.fldCode);
    });

    it('В поле "Код из смс" вводим код невалидный код', () => {
        phonePage.confirmCode('888888');
        phonePage.alertCodeSent.waitForDisplayed();
        assert.equal('Неправильный код', phonePage.alertCodeSent.getText());
        phonePage.btnNext.waitForClickable({ reverse: true });
    });
});
