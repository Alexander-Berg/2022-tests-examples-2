const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" с get-параметром ticket_id', () => {
    it('открыть страницу ?ticket_id=19745623', () => {
        page.open('/?ticket_id=19745623');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
