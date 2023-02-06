const dict = require('../../../pagesDict');
const phonePage = new dict.phonePage();

describe('Позитивные проверки поля "Номер телефона"', () => {
    it('открыть страницу и ввести валидный номер', () => {
        phonePage.open();
        phonePage.fillPhoneNumber();
        phonePage.msgPhoneFormatError.waitForDisplayed({ reverse: true });
    });
});
