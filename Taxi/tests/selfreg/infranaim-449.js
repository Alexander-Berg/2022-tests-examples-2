const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;

describe('Позитивные проверки поля "Логин в Telegram" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('В поле "Логин в Telegram" вводим значение "telegram"', () => {
        personalPage.fillTelegrm('telegram');
        personalPage.itemErrorDescription.waitForDisplayed({ reverse: true });
    });

    it('Стираем предыдущее значение и в поле "Логин в Telegram" вводим значение "telegram123123"', () => {
        personalPage.clearWithBackspace(personalPage.fldTelegram);
        personalPage.fillTelegrm('telegram123123');
        personalPage.itemErrorDescription.waitForDisplayed({ reverse: true });
    });
});
