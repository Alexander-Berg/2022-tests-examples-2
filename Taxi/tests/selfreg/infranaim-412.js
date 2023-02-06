const { assert } = require('chai');
const dict = require('../../../pagesDict');
const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');
const getPuppeterPage = require('../../../etc/lib/getPuppeterPage');
const path = '?utm_source=ok_utm_source&advertisement_campaign=вконтакте_рк&utm_campaign=ok_utm_campaign&utm_term=ok_utm_term&utm_content=ok_utm_content&transaction_id=transaction_id666';
const PhonePage = new dict.phonePage();
const startPage = new dict.startPage;
const page = new PageSelfreg();

describe(`Верстка "Стать курьером" с utm_source,advertisement_campaign,utm_campaign,utm_term,utm_content,transaction_id ${path}`, () => {
    it('открыть главную страницу с гет-параметрами', () => {
        page.open(path);
    });

    it('проходим с валидными данными до страницы phone', () => {
        startPage.goNext();
    });

    let postData;
    it('активировать пупэтэр', async () => {
        const page = await getPuppeterPage();
        return page.on('request', request => {
            if (request._method === 'POST' && request._url.includes('/auth/phone/check')) {
                postData = request._postData;
            }
        });
    });
    it('проходим с валидными данными до страницы placement', () => {
        PhonePage.fillPhoneNumber();
        PhonePage.btnGetCode.click();
        PhonePage.confirmCode();
        PhonePage.btnNext.click();
    });
    const regexp = /{"code":"111111","form_completion_id":".{32}","zendesk_ticket_id":null,"data":\[{"id":"utm_source","value":"ok_utm_source"},{"id":"advertisement_campaign","value":"вконтакте_рк"},{"id":"utm_campaign","value":"ok_utm_campaign"},{"id":"utm_term","value":"ok_utm_term"},{"id":"utm_content","value":"ok_utm_content"},{"id":"transaction_id","value":"transaction_id666"}]}/;
    it('проверить тело пост запроса с utm_source,advertisement_campaign,utm_campaign,utm_term,utm_content,transaction_id', () => {
        browser.pause(2000);
        assert.match(postData, regexp);
    });
});
