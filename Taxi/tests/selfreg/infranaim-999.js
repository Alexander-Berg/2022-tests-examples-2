const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;
const getPuppeterPage = require('../../../etc/lib/getPuppeterPage');

describe('Чекать боди пост-запроса /personal-data', () => {
    it('пройти до стрницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить форму', () => {
        personalPage.fillForm();
    });

    let postData;
    it('активировать пупэтэр', async () => {
        const page = await getPuppeterPage();
        return page.on('request', request => {
            if (request._method === 'POST' && request._url.includes('/form/submit')) {
                postData = request._postData;
            }
        });
    });

    const regexp = /{"data":\[{"id":"date_birth","value":"2000-09-10T20:00:00\.000Z"},{"id":"contact_email","value":"dsa@wqe\.zxc"},{"id":"telegram_name","value":"vasya"},{"id":"name","value":"Кастромской Марк Кастянович"}],"form_completion_id":".{32}","is_finished":true}/
    it('отправить форму', () => {
        personalPage.goNext();
        browser.pause(2000);
        assert.match(postData, regexp);
    });
});
