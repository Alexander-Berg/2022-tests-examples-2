const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 5000;

describe('Выгрузка списка водителей в файл CSV', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('Применить фильтр "Yandex" (чтобы уменьшить список выгрузки)', () => {
        DriversPage.workConditionsDropdown.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.workConditionsDropdown.click();
        DriversPage.selectDropdownItem('Yandex');
        browser.keys('Escape');
        browser.pause(2000);
    });

    it('Убедиться, что при указаных фильтрах отображаются записи водителей', () => {
        DriversPage.getRowInTable().driverTerms.waitForDisplayed({timeout: timeToWaitElem});
    });

    it('Нажать на кнопку загрузки в правом верхнем углу страницы', () => {
        DriversPage.download.downloadReportButton.click();
        DriversPage.download.modalWindow.window.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.download.modalWindow.encodings.inputCP1251.waitForDisplayed({timeout: timeToWaitElem});
        assert.isTrue(DriversPage.download.modalWindow.encodings.inputUTF8.isDisplayed());
        assert.isTrue(DriversPage.download.modalWindow.encodings.inputMacCyrillic.isDisplayed());
        assert.isTrue(DriversPage.download.modalWindow.btnDownload.isDisplayed());
        assert.isTrue(DriversPage.download.modalWindow.btnCancel.isDisplayed());
    });

    it('Нажать "Отмена"', () => {
        DriversPage.download.modalWindow.btnCancel.click();
        assert(DriversPage.download.modalWindow.window.waitForDisplayed({timeout: timeToWaitElem, reverse: true}));
    });

    it('Скачать во всех кодировках (UTF-8, CP1251, MacCyrillic)', () => {
        for (const encoding in DriversPage.download.modalWindow.encodings) {
            DriversPage.download.downloadReportButton.waitForDisplayed({timeout: timeToWaitElem});
            DriversPage.download.downloadReportButton.click();
            DriversPage.download.modalWindow.window.waitForDisplayed({timeout: timeToWaitElem});
            DriversPage.download.modalWindow.encodings[encoding].waitForDisplayed({timeout: timeToWaitElem});
            assert.isTrue(DriversPage.checkFileDownload(DriversPage.download.modalWindow.encodings[encoding], DriversPage.download.modalWindow.btnDownload));
        }
    });
});
