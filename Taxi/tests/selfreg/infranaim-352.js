const { assert } = require('chai');
const dict = require('../../../pagesDict');
const vehiclePage = new dict.vehiclePage;
const getPuppeterPage = require('../../../etc/lib/getPuppeterPage');

describe('Отправка данных по нажатию кнопки "Дальше" со страницы /vehicle-type (Авто)', () => {
    it('пройти до страницы /vehicle-type', () => {
        vehiclePage.open();
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
        vehiclePage.goNext();
    });

    const regexp = /{"data":\[{"id":"courier_transport_type","value":"pedestrian"}\],"form_completion_id":".{32}","is_finished":false}/
    it('проверить тело пост запроса без телеги', () => {
        browser.pause(2000);
        assert.match(postData, regexp);
    });
});
