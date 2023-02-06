const { assert } = require('chai');
const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Негативные проверки поля "номер телефона"', () => {
    it('Открыть страницу /phone', () => {
        phonePage.open();
    });

    if (process.env.MOBILE !== 'true') {
        it('Кнопки неактивны при пустом поле телефона', () => {
            assert.isFalse(phonePage.btnGetCode.isClickable());
            assert.isFalse(phonePage.btnNext.isClickable());
        });
    }

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
