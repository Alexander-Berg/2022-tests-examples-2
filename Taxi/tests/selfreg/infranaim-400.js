const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" с get-параметром utm_content', () => {
    it('открыть страницу ?utm_content=utm_content', () => {
        page.open('/?utm_content=ok_utm_content');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
