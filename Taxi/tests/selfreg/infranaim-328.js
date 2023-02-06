const { assert } = require('chai');
const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');

describe('Позитивные проверки поля "Кода из смс"', () => {
    it('отправить код на телефон', () => {
        phonePage.open();
        phonePage.fillPhoneNumber();
        phonePage.confirmCode();
    });

    it('отображается сообщение подтвержденном коде', () => {
        assert.equal('Номер телефона подтвержден', phonePage.alertCodeSent.getText(), 'Ошибка при подтверждении кодом');
        assert.equal('Можете проходить дальше', phonePage.alertCodeSentDesc.getText(), 'Ошибка при подтверждении кодом');
    });
});
