const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: обновление таблицы', () => {

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на кнопку в виде зацикленной стрелки возле настройки колонок', () => {
        browser.setupInterceptor();
        SignalQDrivers.refreshButton.click();
        browser.pause(2000);
    });

    it('Отправился запрос /list', () => {
        const requests = browser.getRequests();
        const listRequest = requests.find(el => el.url.includes('/api/fleet/signal-device-api-admin/v1/drivers/list'));
        const response = listRequest.response.statusCode;
        expect(response).toEqual(200);
    });
});
