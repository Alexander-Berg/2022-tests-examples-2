const AutosPage = require('../page/AutosPage');
const {assert} = require('chai');

describe('Смоук: скачать отчет по автомобилям', () => {
    it('открыть список водителей', () => {
        AutosPage.goTo();
    });

    it('начать загрузку файла и проверить ответ сервера', () => {
        assert.isTrue(AutosPage.checkFileDownload(AutosPage.downloadReportButton, AutosPage.acceptDownloadButton));
    });
});
