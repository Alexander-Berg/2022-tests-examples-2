const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');
const dict = require('../../../pagesDict');
const page = new PageSelfreg();



describe('Наличие элементов страницы "Стать курьером" с принудительным выбором вакансии', () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open('/?vacancy=shop_pedestrian');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
