const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');
const startPage = require('../../pageobjects/selfreg/page.selfreg.start');
const PhonePage = require('../../pageobjects/selfreg/page.selfreg.phone');
const PlacementPage = require('../../pageobjects/selfreg/page.selfreg.placement');
const page = new PageSelfreg();

describe('Наличие элементов страницы "Стать курьером" с принудительным выбором вакансии', () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open('/?vacancy=shop_pedestrian');
    });
    it('проходим с валидными данными до страницы phone', () => {
        startPage.goNext();
        PhonePage.fillPhoneNumber();
        PhonePage.fillCode();
    });
    it('проходим с валидными данными до страницы placement', () => {
        PhonePage.goNext();
        PlacementPage.goNext();
    });

    // it('сравниваем скриншот страницы с ожидаемым', () => {
    //     page.checkScreenshot('selfreg-shopVacancy')
    // })
});
