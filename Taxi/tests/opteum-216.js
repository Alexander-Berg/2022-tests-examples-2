const RegularCharges = require('../page/RegularCharges');
const {assert} = require('chai');

describe('Смоук: скачать отчет по периодическим списаниям', () => {
    it('открыть список водителей', () => {
        RegularCharges.goTo();
    });

    it('начать загрузку файла и проверить ответ с сервера', () => {
        assert.isTrue(RegularCharges.checkSyncFileDownload(
            RegularCharges.downloadReportButton,
            RegularCharges.acceptDownloadButton,
            undefined,
            'fleet-reports-storage',
        ));
    });
});
