const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" с get-параметром transaction_id', () => {
    it('открыть страницу ?transaction_id=ok_transaction_id666', () => {
        page.open('/?transaction_id=ok_transaction_id666');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
