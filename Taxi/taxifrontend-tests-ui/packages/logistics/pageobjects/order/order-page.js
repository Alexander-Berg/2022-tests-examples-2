const {authorize} = require('../../support/auth');
const pinDropSuggest = require('../../fixtures/suggest/suggest-pin-drop.json');
const {fillAddress} = require('../../support/helpers');

module.exports = {
    myOrdersTab: '//*[text()="Мои заказы"]/..',
    courierTariffBtn: '[value="courier"]',
    expressTariffBtn: '[value="express"]',
    cargoTariffBtn: '[value="cargo"]',
    recipientPhone: '//label[text()="Номер получателя"]',
    addressFrom: '//label[text()="Адрес отправителя"]/..//input',
    addressFromPorchnumber: '//label[text()="Подъезд"]/..//input',
    addressFromFloorNumber: '//label[text()="Этаж"]/..//input',
    addressFromQuartersNumber: '//label[text()="Квартира"]/..//input',
    addressFromDoorphoneNumber: '//label[text()="Домофон"]/..//input',
    addressTo: '(//label[text()="Адрес получателя"]/..//input)[1]',
    addressToSecond: '(//label[text()="Адрес получателя"]/..//input)[2]',
    addAddressBtn: '//*[text()="Добавить адрес доставки"]/..',
    clearAddressBtnFirst: '(//*[text()="Очистить"])[1]',
    clearAddressBtnSecond: '(//*[text()="Очистить"])[2]',
    paymethodCash: '//*[text()="Наличные"]/..',
    addCardBtn: '//*[text()="Привязать карту"]/.',
    cardNumber: '//*[@class="card_number-input"]//input',
    cardValidMonth: '[name="expiration_month"]',
    cardValidYear: '[name="expiration_year"]',
    cardCvn: '[name="cvn"]',
    cardAcceptBtn: '//*[text()="Привязать"]',
    modalAddCardBtn: '//*[text()="Добавить карту"]/.',
    senderNumber: '//*[text()="Номер отправителя"]/..//input',
    recipientNumber: '//*[text()="Номер получателя"]/..//input',
    cancelBtn: '//*[text()="Отменить"]',
    dontCancelModalBtn: '//*[text()="Не отменять"]/..',
    cancelModalBtn: '//*[text()="Отменить заказ"]/..',
    tagMaps: '//ymaps',
    addLoadersBtn: '(//*[text()="Грузчики"]/../..//button)[2]',

    async open(url) {
        // сетим куку для геолокации мск, важно сетить на том же домене, поэтому сначала открывается яндекс
        // куку для другого города можно получить на /tune/geo
        await browser.url('https://yandex.ru/tune/geo');
        await browser.setCookies({
            name: 'yandex_gid',
            value: '213',
            domain: '.yandex.ru',
            secure: true,
            sameSite: 'None'
        });

        await browser.url(url);
    },

    async mockSuggestToMoscow() {
        // в гриде перекидывает на неподдерживаемую локацию, мокаем ручку "саджест" на мск
        const mockSuggest = await browser.mock('**/integration/turboapp/v1/suggest', {
            postData: data => typeof data === 'string'
        });
        mockSuggest.respond(request => {
            let requestAction = JSON.parse(request.postData).action;
            if (requestAction === 'pin_drop') {
                return pinDropSuggest;
            }
        });
    },

    async authorizeAndOpen(url) {
        const loginUser = 'corp-logisticauto41902';
        await this.open(
            `https://passport-test.yandex.ru/auth?new=0&retpath=${browser.config.baseUrl}${url}`
        );
        let authorized = await browser.$(`//*[text()="${loginUser}@yandex.ru"]`).isExisting();
        if (authorized) {
            await browser.url(browser.config.baseUrl + url);
        } else {
            await authorize(loginUser);
            await expect(browser).toHaveUrlContaining(browser.config.baseUrl, {wait: 15000});
        }
    },

    async clickAddAddressBtnTimes(times) {
        await browser.pause(1500);
        for (let n = 1; n <= times; n++) {
            await browser.$(this.addAddressBtn).scrollIntoView();
            await browser.$(this.addAddressBtn).click();
        }
    },

    async waitTabOpen(timeout) {
        let wait = 0;
        let hint = 300;
        let handles;
        while (wait < timeout) {
            handles = await browser.getWindowHandles();
            if (handles.length < 2) {
                await browser.pause(hint);
                wait += hint;
            } else {
                break;
            }
        }
        return handles;
    },

    async fillOrderFields(fields) {
        let orderFields = fields || {
            addressFrom: 'Новосибирск Ленина 12',
            addressFromSuggest: 'улица Ленина, 12',
            senderNumber: '9991233212',
            addressTo: 'новосибирск орджоникидзе 30',
            addressToSuggest: 'улица Орджоникидзе, 30',
            recipientNumber: '9994561222'
        };

        await fillAddress(
            this.addressFrom,
            orderFields.addressFromSuggest,
            orderFields.addressFrom
        );
        await fillAddress(this.addressTo, orderFields.addressToSuggest, orderFields.addressTo);
        await browser.$(this.senderNumber).setValue(orderFields.senderNumber);
        if (orderFields.recipientNumber) {
            await browser.$(this.recipientNumber).setValue(orderFields.recipientNumber);
        }
        await browser.pause(1500);
    },

    async clickOrderBtn() {
        // поиск кнопки с текстом "Заказать・", тк для возможности заказать нужен рассчитанный заказ
        // а когда на кнопке меняется текст с "Заказать" на "Заказать・106р", то заказ рассчитан
        await browser.$('//*[contains(text(),"Заказать・")]').click();
        await browser.pause(3000);
    },

    async cancelOrder() {
        await browser.$(this.cancelBtn).click();
        await browser.pause(1000);
        await browser.$(this.cancelModalBtn).click();
    }
};
