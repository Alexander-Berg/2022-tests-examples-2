const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы service-lavka', () => {
    it('открыть страницу /service-lavka', () => {
        page.open('/service-lavka');
    });

    it('сравниваем скриншот selfreg-lavkaVacancy', () => {
        page.checkScreenshot('selfreg-lavkaVacancy');
    });
});
