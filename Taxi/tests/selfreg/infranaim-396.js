const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" с get-параметром advertisement_campaign', () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open('/?advertisement_campaign=вконтакте_рк');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
