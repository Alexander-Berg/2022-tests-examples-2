const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" с get-параметром utm_campaign', () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open('/?utm_campaign=ok_utm_campaign');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
