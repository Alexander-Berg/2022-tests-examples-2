const { assert } = require('chai');
const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');

describe('Негативные проверки поля "номер телефона"', () => {
    it('Открыть страницу /phone', () => {
        phonePage.open();
    });

    it('Кнопки неактивны при пустом поле телефона', () => {
        assert.isFalse(phonePage.btnGetCode.isClickable());
        assert.isFalse(phonePage.btnNext.isClickable());
    });

    it('Отправить код на номер 8888888888', () => {
        phonePage.fillPhoneNumber('8888888888');
        phonePage.btnGetCode.click();
    });

    it('отобразился алерт с текстом ошибки', () => {
        phonePage.alertCodeSent.waitForDisplayed();
        assert.equal(phonePage.alertCodeSent.getText(), 'Введён некорректный номер телефона');
        assert.equal(phonePage.alertCodeSentDesc.getText(), 'Попробуйте ввести другой');
    });
});
