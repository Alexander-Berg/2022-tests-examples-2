const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const VehicleTab = require('../../page/driverCard/VehicleTab');
const {_generateRandomCarNumber} = require('../../page/AutoCard');

const getRandomInt = (min, max) => {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min)) + min; // Максимум не включается, минимум включается
};

const testData = {
    details: {
        status: 'Не работает',
        mark: 'BMW',
        model: '7er',
        color: 'Черный',
        year: '2021',
        number: _generateRandomCarNumber().toUpperCase(),
        vin: `11122233344${getRandomInt(100_000, 999_999)}`,
        bodyNumber: `11122233344${getRandomInt(100_000, 999_999)}`,
        sts: '1',
        license: '1',
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
        codeName: 't005st',
    },
    options: 'WiFi',
    categories: 'Бизнес',
    tariffs: 'abc',
};

const timeToWaitElem = 30_000;
const driverName = 'opteum-109';

describe('Карточка водителя: привязка нового авто', () => {
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
    });

    it('Выбрать "Новый"', () => {
        VehicleTab.choiceInputs.label.waitForDisplayed({timeout: timeToWaitElem});
        VehicleTab.choiceInputs.new.click();
    });

    it('Заполнить карточку авто данными', () => {
        VehicleTab.waitingLoadThisPage(timeToWaitElem);
        VehicleTab.fillAllFields(testData);
    });

    it('Нажать кнопку "Сохранить"', () => {
        DriverCard.saveButton.click();
        browser.pause(1000);
    });

    it('Обновить страницу', () => {
        // !FIXME: не использовать бесконечный цикл
        // eslint-disable-next-line no-constant-condition
        while (true) {
            browser.refresh();

            try {
                VehicleTab.waitingLoadThisPage(timeToWaitElem);
                break;
            } catch {
                browser.pause(1000);
            }
        }

        VehicleTab.checkAllFields(testData);
    });

    it('Отвязать авто', () => {
        VehicleTab.btnUnlinkAuto.btn.waitForDisplayed({timeout: timeToWaitElem});
        VehicleTab.btnUnlinkAuto.btn.click();
        VehicleTab.btnUnlinkAuto.modalWindow.window.waitForDisplayed();
        VehicleTab.btnUnlinkAuto.modalWindow.btnYes.click();
        browser.pause(2000);
    });
});
