const { assert } = require('chai');
const dict = require('../../../pagesDict');
const personalPage = new dict.personalPage;
const getPuppeterPage = require('../../../etc/lib/getPuppeterPage');

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /personal-data (без телеги)', () => {
    it('пройти до страницы /personal-data', () => {
        personalPage.open();
    });

    it('заполнить форму', () => {
        personalPage.fillForm();
    });

    it('очистить Телеграмм', () => {
        personalPage.clearWithBackspace(personalPage.fldTelegram);
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

    it('пройти далее', () => {
        personalPage.goNext();
    });

    const regexp = /{"data":\[{"id":"date_birth","value":"2000-09-10T20:00:00\.000Z"},{"id":"contact_email","value":"dsa@wqe\.zxc"},{"id":"name","value":"Кастромской Марк Кастянович"}],"form_completion_id":".{32}","is_finished":true}/
    it('проверить тело пост запроса без телеги', () => {
        browser.pause(2000);
        assert.match(postData, regexp);
    });
});
