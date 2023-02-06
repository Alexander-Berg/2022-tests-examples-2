const {authorize} = require('../../support/auth');
const {fillAddress} = require('../../support/helpers');

module.exports = {
    statusInput: '//*[text()="Статус заявки"]',
    fromInput: '[placeholder="От"]',
    toInput: '[placeholder="До"]',
    claimIdInput: '[placeholder="ID заказа/Номер телефона"]',
    exportBtn: '//*[text()="Экспорт"]',
    uploadFileBtn: '//*[text()="Загрузить файл"]',
    createClaimBtn: '//*[text()="Создать заказ"]',
    firstClaimInList: '(//*[@class="RowGroup"]/div)[1]',
    editBtn: '(//a[contains(@class,"MuiButtonBase-root MuiIconButton-root")])[2]',
    cargoOrderForm: '.CargoOrderForm',
    closeFormBth: '.ModalCloseButton',
    okModalCloseForm: '//*[text()="ОК"]',
    addressFromInput: '(//*[@placeholder="Адрес"])[1]',
    senderNameInput: '[placeholder="Имя отправителя"]',
    addAddressBtn: '(//*[text()="Добавить"])[1]',
    senderEmailInput: '[placeholder="E-mail"]',
    senderPhoneInput: '[placeholder="Телефон отправителя"]',
    addressToInput: '(//*[@placeholder="Адрес"])[2]',
    addressTo2Input: '(//*[@placeholder="Адрес"])[3]',
    addressTo3Input: '(//*[@placeholder="Адрес"])[4]',
    optimizeRouteBtn: '//*[text()="Оптимизировать маршрут"]',
    recipientNameInput: '[placeholder="Имя получателя"]',
    recipientNumberInput: '[placeholder="Телефон получателя"]',
    itemNameInput: '[placeholder="Наименование"]',
    widthInput: '[name="items.0.size.width"]',
    heightInput: '[name="items.0.size.height"]',
    lengthInput: '[name="items.0.size.length"]',
    weightInput: '[name="items.0.weight"]',
    countItemInput: '[placeholder="Кол-во*"]',
    addressSelector: '//*[@class="Select-control"]',
    selectExpressTariffBtn: '(//*[text()="Выбрать"])[2]',
    createClaimFormBtn: '//*[@class="CargoOrderForm"]//*[text()="Создать заказ"]',
    acceptClaimFormBtn: '//*[@class="CargoOrderForm"]//*[text()="Подтвердить"]',
    closeMessageBtn: '//*[@class="Notification__messenger"]//*[@aria-label="close"]',
    autoAssignmentCheckbox: '//*[@name="autoAssignment"]/../span',

    async authorizeAndOpenCargo() {
        const loginUser = 'corp-logisticauto41902';
        await browser.url(
            `https://passport-test.yandex.ru/auth?new=0&origin=b2b_dostavka&retpath=${browser.config.baseUrl}/account`
        );
        await authorize(loginUser);
        //Проверяем, что страница загрузилась и обновляем ее, чтобы выставился параметр timezone в localStorage
        await browser.$('//*[text()="Меню"]').waitForDisplayed();
        // Устанавливаем русский язык
        await browser.setCookies({
            name: 'lang',
            value: 'ru'
        });
        await browser.refresh();
        await browser.pause(1000);

        await browser.$('[href="/account/cargo"]').click();
    },

    async fillClaimForm(fields) {
        let claimFields = fields || {
            addressFrom: 'Новосибирск Ленина 12',
            addressFromSuggest: 'улица Ленина, 12',
            senderName: 'Отправитель тест',
            senderEmail: 'sendertest@sobak.rte',
            senderPhone: '+79991234589',
            addressTo: 'новосибирск орджоникидзе 30',
            addressToSuggest: 'улица Орджоникидзе, 30',
            recipientName: 'Получатель тест',
            recipientNumber: '+79991236743',
            itemName: 'Коробка нормальная',
            countItem: '2'
        };

        await browser.$(this.createClaimBtn).click();
        await browser.$(this.cargoOrderForm).waitForDisplayed();

        await fillAddress(
            this.addressFromInput,
            claimFields.addressFromSuggest,
            claimFields.addressFrom
        );
        await browser.$(this.senderNameInput).setValue(claimFields.senderName);
        await browser.$(this.senderEmailInput).setValue(claimFields.senderEmail);
        await browser.$(this.senderPhoneInput).setValue(claimFields.senderPhone);

        await fillAddress(this.addressToInput, claimFields.addressToSuggest, claimFields.addressTo);
        await browser.$(this.recipientNameInput).setValue(claimFields.recipientName);
        await browser.$(this.recipientNumberInput).setValue(claimFields.recipientNumber);

        await browser.$(this.itemNameInput).setValue(claimFields.itemName);
        await browser.$(this.countItemInput).setValue(claimFields.countItem);
        await browser.$(this.addressSelector).click();
        await browser.$('.Select-menu-outer').click();
    }
};
