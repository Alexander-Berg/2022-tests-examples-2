const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" с get-параметром utm_source', () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open('/?utm_source=ok_utm_source');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
