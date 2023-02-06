const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы service-delivery', () => {
    it('открыть страницу /service-delivery', () => {
        page.open('/service-delivery');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-taxiDeliveryVacancy');
    });
});
