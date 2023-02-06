const DriverCard = require('../../page/driverCard/DriverCard');
const VehicleTab = require('../../page/driverCard/VehicleTab');

const timeToWaitElem = 5000;
const driverName = 'opteum-103';
const autoNumber = 'Т004СТ01';
const autoAllInfo = 'Т004СТ01 :: BMW 7er 2021 Черный :: Работает';

const autoSearchInput = () => $('div[class*="VehiclesTab_container"] div.Select__input input');

const searchAuto = (number, allInfo) => {
    autoSearchInput().setValue(number);
    browser.pause(1000);
    VehicleTab.selectDropdownItem(allInfo);
    browser.keys('Escape');
};

describe('Карточка водителя: перепривязка автомобиля', () => {

    it(`Открыть раздел "Автомобиль" в карточке водителя ${driverName}`, () => {
        DriverCard.open('/drivers/8c39661ccc81fbd9d67f284b59606a0a/car');

        try {
            VehicleTab.waitingLoadThisPage(timeToWaitElem);
        } catch {
            VehicleTab.autoSearchDropdown.waitForDisplayed();
            searchAuto(autoNumber, autoAllInfo);
            VehicleTab.btnChangeAuto.waitForDisplayed();
            VehicleTab.btnChangeAuto.click();
            browser.pause(2000);
            $('span=Открепить').waitForDisplayed();
            browser.refresh();
        }
    });

    it('Открепить автомобиль', () => {
        VehicleTab.btnUnlinkAuto.btn.waitForDisplayed();
        VehicleTab.btnUnlinkAuto.btn.click();
        VehicleTab.btnUnlinkAuto.modalWindow.window.waitForDisplayed();
        VehicleTab.btnUnlinkAuto.modalWindow.btnYes.click();
        browser.pause(2000);
    });

    it('Обновить страницу', () => {
        browser.refresh();
        browser.pause(2000);
        VehicleTab.autoSearchDropdown.waitForDisplayed();
    });

    it('отсутствует прикрепленный автомобиль', () => {
        expect(VehicleTab.btnUnlinkAuto.btn).not.toBeDisplayed();
    });

    it('Найти автомобиль через поисковую строку', () => {
        searchAuto(autoNumber, autoAllInfo);
    });

    it('Нажать кнопку "Сменить автомобиль"', () => {
        VehicleTab.btnChangeAuto.waitForDisplayed();
        VehicleTab.btnChangeAuto.click();
        browser.pause(2000);
        $('span=Открепить').isDisplayed();
    });

    it('Обновить страницу', () => {
        browser.refresh();
        browser.pause(1000);
    });

    it('Отображается привязанный на шаге 5 автомобиль', () => {
        VehicleTab.waitingLoadThisPage(timeToWaitElem);
        expect(VehicleTab.btnUnlinkAuto.btn).toBeDisplayed();
    });
});
