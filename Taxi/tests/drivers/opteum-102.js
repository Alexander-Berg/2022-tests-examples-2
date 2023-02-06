const DriversPage = require('../../page/DriversPage');
const RegularCharges = require('../../page/RegularCharges');
const {assert} = require('chai');

const timeToWaitElem = 25_000;
const driverId = '2070b8862d63021e211c1fc2bd8e6792';

const testData = {
    driver: 'opteum-102',
    vehicle: 'А111АА11',
    amount: '5',
};

let driverRegularChargesCount;

// !FIXME: выше уже есть константа с таким названием
// eslint-disable-next-line no-shadow
const openDriverCharges = driverId => {
    DriversPage.open(`/drivers/${driverId}/regular_charges`);
    browser.pause(2000);
    const firstCellInTable = 'tr td:nth-child(1)';
    $(`${firstCellInTable}`).waitForDisplayed({timeout: timeToWaitElem});
};

describe('Карточка водителя: периодические списания', () => {

    it('Открыть периодические списания в карточке водителя', () => {
        openDriverCharges(driverId);
    });

    it('Запомнить существующие периодические списания', () => {
        [driverRegularChargesCount] = $('[class*=Total_aggregate]').getText().split(' ');
    });

    it('Открыть список периодических списаний парка', () => {
        browser.url('https://fleet.tst.yandex.ru/regular-charges?park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru');
    });

    it('Добавить периодическое списание водителю', () => {
        RegularCharges.addChargesButton.waitForDisplayed({timeout: timeToWaitElem});
        RegularCharges.addChargesButton.click();

        try {
            RegularCharges.warningMaxCharges.warning.waitForDisplayed({timeout: 1500, reverse: true});
        } catch {
            RegularCharges.warningMaxCharges.btnOk.click();
            RegularCharges.deleteChargesFromList();
            RegularCharges.addChargesButton.waitForDisplayed({timeout: timeToWaitElem});
            RegularCharges.addChargesButton.click();
        }

        RegularCharges.waitingLoadThisPage(timeToWaitElem);
        RegularCharges.addChargesByRequiredFields(testData);
        RegularCharges.doneAlert.waitForDisplayed({timeout: timeToWaitElem});
    });

    it('Открыть периодические списания в карточке водителя', () => {
        openDriverCharges(driverId);
    });

    it('Проверить, что количество списаний увеличилось на 1', () => {
        const newDriverRegularChargesCount = $('[class*=Total_aggregate]').getText().split(' ');
        assert.isTrue(newDriverRegularChargesCount > driverRegularChargesCount);
    });

    it('Удалить списание', () => {
        browser.url('https://fleet.tst.yandex.ru/regular-charges?park_id=7ad36bc7560449998acbe2c57a75c293&lang=ru');
        RegularCharges.addChargesButton.waitForDisplayed({timeout: timeToWaitElem});
        RegularCharges.deleteChargesFromList();
    });
});
