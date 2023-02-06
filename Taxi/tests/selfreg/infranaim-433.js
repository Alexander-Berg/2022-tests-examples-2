const { assert } = require('chai');
const { processors } = require('xml2js');
const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Негативные проверки поля "кода из смс"', () => {
    it('пройти до страницы /phone', () => {
        phonePage.open();
    });

    it('заполнить телефон и отправить код', () => {
        phonePage.fillPhoneNumber();
        phonePage.btnGetCode.click();
        // refresh page for closing popup
        // eslint-disable-next-line no-undef
        if (process.env.MOBILE !== 'true') {
            browser.refresh();
        }
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
