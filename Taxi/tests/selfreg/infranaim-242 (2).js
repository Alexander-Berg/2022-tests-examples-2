const { assert } = require('chai');
const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Отправка данных по нажатию кнопки "Получить код"', () => {
    if (process.env.MOBILE !== 'true') {
        it('Отправить код на телефон', () => {
            phonePage.open();
            phonePage.fillPhoneNumber();
            phonePage.btnGetCode.click();
        });

        it('отображается сообщение о таймере повторной отправки кода', () => {
            phonePage.msgSendCodeTimeout.waitForDisplayed();
            assert.match(phonePage.msgSendCodeTimeout.getText(), /До новой попытки [0-9]{1,2} с\./, 'Ошибка в тексте таймаута повторной отправки смс');
        });

        it('отобрзился алерт о успешной отправке', () => {
            phonePage.alertCodeSent.waitForDisplayed();
            assert.equal('Код успешно отправлен на телефон', phonePage.alertCodeSent.getText(), 'Ошибка в тексте об успешной отправке смс');
        });

        it('кнопка отправки кода стала неактивной', () => {
            phonePage.btnGetCode.waitForClickable({ reverse: true });
        });
    }
});
