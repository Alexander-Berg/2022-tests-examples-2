const AutoCard = require('../../page/AutoCard');
const autosPage = require('../../page/AutosPage');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');

let uniqueCarNumber;

describe('Карточка водителя: привязать новый автомобиль', () => {
    it('Открыть страницу автомобилей', () => {
        autosPage.goTo();
    });

    it('Нажать кнопку добавления автомобиля', () => {
        autosPage.addButton.click();
    });

    it('заполнить обязательные поля', () => {
        uniqueCarNumber = AutoCard.fillRequiredData();
    });

    it('открыть список автомобилей', () => {
        autosPage.goTo();
    });

    it('в списке есть созданный автомобиль', () => {
        browser.waitUntil(() => {
            browser.refresh();
            $('tr').waitForDisplayed();
            const nicknames = $$('[class*=SignCell_cell]').map(el => el.getText());
            return nicknames.includes(uniqueCarNumber);
        });
    });

    it('открыть страницу водителей и найти водителя 2883945683', () => {
        DriversPage.goTo();
        DriversPage.searchField.waitForClickable();
        DriversPage.searchField.click();
        browser.keys('2883945683');
        browser.waitUntil(() => $$('main tbody tr').length === 1);
    });

    it('открыть карточку водителя и открепить автомобиль если он есть', () => {
        $('span=Работает').click();
        DriverCard.driverAutoTab.waitForDisplayed();
        DriverCard.driverAutoTab.click();
        $('h4=Выбор автомобиля').waitForDisplayed();

        if ($('[class*=buttonDetach]').isDisplayed()) {
            $('[class*=buttonDetach]').click();
            $('span=Да').click();
            browser.refresh();
        }
    });

    it('привязать созданный автомобиль', () => {
        $('[class*=BindExistingVehicle_selector__]').click();
        $('[class*=BindExistingVehicle_selector__]').waitForEnabled();

        browser.keys(uniqueCarNumber);
        browser.waitUntil(() => DriverCard.selectOption.length > 0);
        browser.keys('Enter');
        $('span=Сменить автомобиль').click();

        $('span=Открепить').waitForDisplayed;

    });

    it('автомобиль отображается в списке водителей', () => {
        browser.waitUntil(() => {
            DriversPage.goTo();
            DriversPage.searchField.click();
            browser.keys('2883945683');
            browser.waitUntil(() => $$('main tbody tr').length === 1);
            return $$('[class*=CallSignCell_cell]')[0].getText() === uniqueCarNumber;
        });

    });
});
