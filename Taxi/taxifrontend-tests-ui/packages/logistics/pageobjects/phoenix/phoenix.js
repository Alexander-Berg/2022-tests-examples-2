const {authorize} = require('../../support/auth');
const {fillAddress} = require('../../support/helpers');

module.exports = {
    filterFromInput: '[placeholder="От"]',
    filterToInput: '[placeholder="До"]',
    filterClaimIdInput: '[placeholder="ID или телефон"]',
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
    recipient2NameInput: '(//*[@placeholder="Имя получателя"])[2]',
    recipientNumberInput: '[placeholder="Телефон получателя"]',
    recipient2NumberInput: '(//*[@placeholder="Телефон получателя"])[2]',
    itemNameInput: '[name="items.0.name"]',
    item2NameInput: '[name="items.1.name"]',
    widthInput: '[name="items.0.size.width"]',
    heightInput: '[name="items.0.size.height"]',
    lengthInput: '[name="items.0.size.length"]',
    weightInput: '[name="items.0.weight"]',
    countItemInput: '[name="items.0.quantity"]',
    countItem2Input: '[name="items.1.quantity"]',
    addressSelector: '//*[@class="Select-control"]',
    address2Selector: '(//*[@class="Select-control"])[2]',
    address2SelectorInput: '(//*[@class="Select-control"]//input)[2]',
    addItemBtn: '(//*[text()="Добавить"])[2]',
    selectCourierTariffBtn: '(//*[text()="Выбрать"])[1]',
    selectExpressTariffBtn: '(//*[text()="Выбрать"])[2]',
    createClaimFormBtn: '//*[@class="CargoOrderForm"]//*[text()="Создать заказ"]',
    acceptClaimFormBtn: '//*[@class="CargoOrderForm"]//*[text()="Подтвердить"]',
    closeMessageBtn: '//*[@class="Notification__messenger"]//*[@aria-label="close"]',
    autoAssignmentCheckbox: '//*[@name="autoAssignment"]/../span',

    async authorizeAndOpenCargo(login) {
        const loginUser = login || 'phoenix-autotest';
        await browser.url(
            `https://passport-test.yandex.ru/auth?new=0&origin=b2b_dostavka&retpath=${browser.config.baseUrl}/account2`
        );
        let authorized = await browser.$(`//*[text()="${loginUser}@yandex.ru"]`).isExisting();
        if (authorized) {
            await browser.url(`${browser.config.baseUrl}/account2`);
        } else {
            await authorize(loginUser);
            await browser
                .$('//*[text()="Выберите компанию для входа"]')
                .waitForExist({timeout: 20000});
            await browser.$(`//*[text()="${loginUser}"]`).click();
        }
        //Проверяем, что страница загрузилась и обновляем ее, чтобы выставился параметр timezone в localStorage
        await browser.$('//*[text()="Меню"]').waitForDisplayed();
        // Устанавливаем русский язык
        await browser.setCookies({
            name: 'lang',
            value: 'ru'
        });
        await browser.refresh();
        await browser.pause(1000);

        await browser.$('[href="/account2/cargo"]').click();
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
    },

    async waitUnlockClaimForm() {
        // ожидание разблокировки полей и кнопки формы, считаем что после этого заявка рассчитана
        await browser.$('.amber-button_disabled').waitForExist({reverse: true, timeout: 30000});
        await browser.pause(1000);
    }
};
