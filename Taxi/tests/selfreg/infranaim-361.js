const personalPage = require('../../pageobjects/selfreg/page.selfreg.personal-data');

describe('Позитивные проверки поля "E-mail" страницы /personal-data', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('В поле "E-mail" вводим "yandex@yandex.ru" ', () => {
        personalPage.fillContactEmail('yandex@yandex.ru');
        personalPage.itemErrorDescription.waitForDisplayed({ reverse: true });
    });
});
