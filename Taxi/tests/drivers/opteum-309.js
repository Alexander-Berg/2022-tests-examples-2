const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const {randomNumLength} = require('../../../../utils/number');
const {sample} = require('lodash');

const timeToWaitElem = 10_000;
const courierName = 'opteum-309';
const courierCodeName = 'COURIERf913b';

const testData = {
    details: {
        phoneNumber: `+${randomNumLength(11)}`,
        status: sample(['Работает', 'Не работает']),
    },
    instantPayouts: sample([1, 10]),
    workRules: {
        workRules: sample(['4Q', '1111']),
        limit: randomNumLength(1),
        dateStart: `1${randomNumLength(1)}.10.2021`,
        checkBoxPlatformOrders: sample([true, false]),
        checkBoxPartnerOrders: sample([true, false]),
        checkBoxCashlessRides: sample([true, false]),
        checkBoxReceipts: sample([true, false]),
    },
    personalDetails: {
        emergencyContact: `+${randomNumLength(11)}`,
        email: `test${randomNumLength(1)}@yandex.ru`,
        address: randomNumLength(1),
        driverFeedback: randomNumLength(1),
        paymentsID: randomNumLength(6),
        notes: randomNumLength(1),
    },
    passportDetails: {
        type: sample(['Национальный паспорт', 'Международный паспорт']),
        country: sample(['Азербайджан', 'Армения']),
        issuedBy: randomNumLength(1),
        address: randomNumLength(1),
        inn: randomNumLength(1),
        numberAndSeries: randomNumLength(1),
        postIndex: randomNumLength(1),
        dateStart: `1${randomNumLength(1)}.10.2021`,
        dateEnd: `1${randomNumLength(1)}.11.2021`,
        ogrn: randomNumLength(1),
    },
    bankDetails: {
        bic: randomNumLength(1),
        settlementAccount: randomNumLength(1),
        correspondentAccount: randomNumLength(1),
    },
};

describe('Редактирование карточки курьера: таб Детали', () => {
    it('Открыть список водителей', () => {
        DriversPage.goTo();
    });

    it(`Перейти в карточку созданного курьера ${courierName}`, () => {
        DriversPage.searchField.waitForDisplayed();
        DriversPage.type(DriversPage.searchField, courierName);
        $(`a*=${courierCodeName}`).waitForDisplayed();
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    Object.entries(testData).forEach(([key, value]) => {
        it(`Отредактировать все поля "${key}"`, () => {
            DetailsTab.fillAllBlocks({[key]: value});
        });
    });

    it('Нажать кнопку "Сохранить"', () => {
        DriverCard.saveButton.click();
        DriverCard.alert.waitForDisplayed();
        expect(DriverCard.alert).toHaveText('Готово');
    });

    it('Обновить страницу', () => {
        browser.refresh();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('Сравнить текущие данные с заполненными раннее', () => {
        DetailsTab.checkAllChangeFields(testData);
    });

});
