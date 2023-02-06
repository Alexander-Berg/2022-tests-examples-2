const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы service-shop', () => {
    it('открыть страницу /service-shop', () => {
        page.open('/service-shop');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-shopVacancy');
    });
});
