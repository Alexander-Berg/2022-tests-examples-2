const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы service-eda', () => {
    it('открыть страницу /service-eda', () => {
        page.open('/service-eda');
    });

    it('сравниваем скриншот selfreg-edaDeliveryVacancy', () => {
        page.checkScreenshot('selfreg-edaDeliveryVacancy');
    });
});
