const { assert } = require('chai');
const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Позитивные проверки поля "Кода из смс"', () => {
    it('отправить код на телефон', () => {
        phonePage.open();
        phonePage.fillPhoneNumber();
        if (process.env.MOBILE === 'true') {
            phonePage.btnGetCode.click();
        }
    });

    it('отображается сообщение после подтверждения кода', () => {
        phonePage.confirmCode();
        phonePage.alertCodeSent.waitForDisplayed();
        assert.equal('Номер телефона подтвержден', phonePage.alertCodeSent.getText());
        assert.equal('Можете проходить дальше', phonePage.alertCodeSentDesc.getText());
    });
});
