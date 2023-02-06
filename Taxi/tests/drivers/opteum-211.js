const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

describe('Смоук: скачать отчет по водителям', () => {
    it('открыть список водителей', () => {
        DriversPage.goTo();
    });

    it('начать загрузку файла и проверить ответ с сервера', () => {
        browser.pause(3000);
        assert.isTrue(DriversPage.checkFileDownload(DriversPage.downloadReportButton, DriversPage.acceptDownloadButton));
    });
});
