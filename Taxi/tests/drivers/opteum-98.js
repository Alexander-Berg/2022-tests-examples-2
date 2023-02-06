const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const VehicleTab = require('../../page/driverCard/VehicleTab');

const testData = {
    details: {
        status: 'Неизвестен',
        bodyNumber: '11122233344455667',
    },
    optionsAndBranding: {
        transmission: 'Автомат',
        boosters: '3',
        childSeats: {
            dropdown: '0',
            seatBrand: '',
            seatGroup: '',
        },
        decalsCheckbox: false,
        lightboxCheckbox: false,
    },
    parameters: {
        license: 'Vasya',
        renta: 'Нет',
        codeName: 't003st',
    },
    options: 'Кондиционер',
    categories: 'Эконом',
    tariffs: '123',
};

const defaultData = {
    details: {
        status: 'Не работает',
        bodyNumber: '11122233344455666',
    },
    optionsAndBranding: {
        transmission: 'Механика',
        boosters: '2',
        childSeats: {
            dropdown: '0',
            seatBrand: '',
            seatGroup: '',
        },
        decalsCheckbox: true,
        lightboxCheckbox: true,
    },
    parameters: {
        license: 'aaa',
        renta: 'Да',
        codeName: 't002st',
    },
    options: 'WiFi',
    categories: 'Бизнес',
    tariffs: 'abc',
};

const timeToWaitElem = 10_000;
const driverName = 'opteum-98';

describe('Карточка водителя: редактирование привязанного автомобиля', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it(`Открыть карточку водителя ${driverName}`, () => {
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(2000);
        DriversPage.getRowInTable().fullName.click();
        DriverCard.waitingLoadThisPage(timeToWaitElem);
    });

    it('Открыть раздел "Автомобиль" в карточке водителя', () => {
        DriverCard.tabs.vehicle.click();
        VehicleTab.waitingLoadThisPage(timeToWaitElem);
    });

    it('Отредактировать значения всех полей на новые', () => {
        VehicleTab.fillAllFields(testData);
    });

    it('Сохранить изменения', () => {
        DriverCard.saveButton.click();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        VehicleTab.waitingLoadThisPage(timeToWaitElem);
        VehicleTab.checkAllFields(testData);
    });

    it('Вернуть дефолтные данные', () => {
        VehicleTab.fillAllFields(defaultData);
        DriverCard.saveButton.click();
        browser.pause(2000);
    });
});
