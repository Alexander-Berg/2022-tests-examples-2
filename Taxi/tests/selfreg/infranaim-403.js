const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');

const page = new PageSelfreg();
describe('Наличие элементов страницы "Стать курьером" со всеми get-параметрами', () => {
    it('открыть страницу ?ticket_id=19745623&transaction_id=transaction_id666&utm_content=ok_utm_content&utm_term=ok_utm_term&utm_source=ok_utm_source&utm_campaign=ok_utm_campaign&advertisement_campaign=вконтакте_рк&vacancy=shop_pedestrian', () => {
        page.open('/?ticket_id=19745623&transaction_id=transaction_id666&utm_content=ok_utm_content&utm_term=ok_utm_term&utm_source=ok_utm_source&utm_campaign=ok_utm_campaign&advertisement_campaign=вконтакте_рк&vacancy=shop_pedestrian');
    });

    it('сравниваем скриншот страницы с ожидаемым', () => {
        page.checkScreenshot('selfreg-welcome');
    });
});
