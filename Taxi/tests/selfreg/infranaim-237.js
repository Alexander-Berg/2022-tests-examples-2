const phonePage = require('../../pageobjects/selfreg/page.selfreg.phone');

describe('Позитивные проверки поля "Номер телефона"', () => {
    it('открыть страницу и ввести валидный номер', () => {
        phonePage.open();
        phonePage.fillPhoneNumber();
        phonePage.msgPhoneFormatError.waitForDisplayed({ reverse: true });
    });
});
