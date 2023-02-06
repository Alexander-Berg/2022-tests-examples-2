module.exports = {
    fileUploadDownloadBtn: '//*[text()="Файл загрузки и выгрузки"]/../..//button',
    downloadFieldsBtn: '//*[text()="Выгрузить поля для заполнения"]/../..//button',
    uploadEmployeesInput: '//*[text()="Выберите файл"]/input',

    async openEmployeesImport(clientId) {
        await browser.url(`/corp-clients/edit/${clientId}/employees-import`);
    }
};
