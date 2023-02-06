const auth = require('../../support/auth');
const page = require('../../pageobjects/corp-clients/employees-import');
const path = require('path');
const allureReporter = require('@wdio/allure-reporter').default;

describe('Загрузка сотрудников', () => {
    before(async () => {
        await auth();
    });

    beforeEach(async () => {
        await page.openEmployeesImport('371fdff9e02245058c0dbe99169749c9');
    });

    it('Выгрузка файла Загрузки и выгрузки. Вкладка Загрузка сотрудников', async () => {
        allureReporter.addTestId('corptaxi-751');
        // не проверяется скачанный файл, проверям что ручка с файлом ответила 200
        const mock = await browser.mock('**/api-t/admin/corp/v1/users/csv/result/**', {
            method: 'GET'
        });

        await browser.$(page.fileUploadDownloadBtn).click();
        await expect(mock).toBeRequestedWith({
            statusCode: 200
        });
    });

    it('Выгрузка полей для заполнения. Вкладка Загрузка сотрудников', async () => {
        allureReporter.addTestId('corptaxi-752');
        // не проверяется скачанный файл, проверям что ручка с файлом ответила 200
        const mock = await browser.mock('**/api-t/admin/corp/v1/users/csv/result/**', {
            method: 'GET'
        });

        await browser.$(page.downloadFieldsBtn).click();
        await expect(mock).toBeRequestedWith({
            statusCode: 200
        });
    });

    it('Загрузка сотрудников. Вкладка Загрузка сотрудников', async () => {
        allureReporter.addTestId('corptaxi-753');

        // загрузка файла в грид с браузером
        const filePath = path.join(__dirname, '/corp-employees-upload.csv');
        const remoteFilePath = await browser.uploadFile(filePath);

        // проверяется, что файл загружается и появляется ошибка валидации
        await browser.$(page.uploadEmployeesInput).setValue(remoteFilePath);
        await expect(
            browser.$('//*[text()="При загрузке сотрудников произошла ошибка"]')
        ).toBeDisplayed();
    });
});
