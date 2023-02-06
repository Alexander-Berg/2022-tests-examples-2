const moment = require('moment');
const ReportDownloadDialog = require('../../page/ReportDownloadDialog');
const Selenoid = require('../../../../utils/api/Selenoid');
const TransferRequests = require('../../page/transferRequests/TransferRequests.js');
const {csvUtf8ParseToArray} = require('../../../../utils/files');

describe('Выгрузка списка заявок на перевод средств', () => {

    const DATA = {
        file: `contractor_instant_payouts_${moment().format('YYYY-MM-DD')}.csv`,
        report: [
            'ID водителя',
            'Водитель',
            'Сумма заявки',
            'Списано с баланса водителя',
            'Списано со счета',
            '№ карты',
            'Дата',
            'Статус',
            'Банк',
            'ID транзакции',
        ],
    };

    let data;

    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('Нажать на кнопку "скачать"', () => {
        TransferRequests.downloadBtn.click();
    });

    it('Открылся диалог сохранения отчёта', () => {
        expect(ReportDownloadDialog.title).toHaveElemVisible();
    });

    it('Переключить кодировку на utf8', () => {
        ReportDownloadDialog.radio.utf8.click();
    });

    it('Нажать на кнопку сохранения отчёта', () => {
        ReportDownloadDialog.buttons.download.click();
    });

    it('Отчёт сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить отчёт', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном отчёте есть данные', () => {
        expect(data.length).toBeGreaterThan(1);
    });

    it('В сохраненном отчёте отображаются корректные колонки', () => {
        expect(data[0]).toEqual(DATA.report);
    });

});
