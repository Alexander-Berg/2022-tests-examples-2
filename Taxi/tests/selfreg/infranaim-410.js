const { assert } = require('chai');
const dict = require('../../../pagesDict');
const PageSelfreg = require('../../pageobjects/selfreg/page.selfreg');
const getPuppeterPage = require('../../../etc/lib/getPuppeterPage');
const path = '/?transaction_id=transaction_id666';
const PhonePage = new dict.phonePage();
const startPage = new dict.startPage;
const page = new PageSelfreg();

describe(`Верстка "Стать курьером" с transaction_id ${path}`, () => {
    it('открыть главную страницу с гет-параметром', () => {
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
    const regexp = /{"code":"111111","form_completion_id":".{32}","zendesk_ticket_id":null,"data":\[{"id":"transaction_id","value":"transaction_id666"}]}/;
    it('проверить тело пост запроса с transaction_id', () => {
        browser.pause(2000);
        assert.match(postData, regexp);
    });
});
