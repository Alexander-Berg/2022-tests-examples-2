const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

const timeToWaitElem = 2000;
const driverName = 'лолов кек';

describe('Очистка поля поиска крестиком', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it(`Указать в поиске имя водителя ${driverName}`, () => {
        DriversPage.searchField.waitForDisplayed({timeout: timeToWaitElem});
        DriversPage.type(DriversPage.searchField, driverName);
        browser.pause(timeToWaitElem);
    });

    it('Очистить поле поиска при помощи кнопки крестика', () => {
        const btnClear = $('header span[class*="Icon"] > svg');
        btnClear.waitForDisplayed({timeout: timeToWaitElem});
        btnClear.click();
        browser.pause(timeToWaitElem);

        assert.isTrue(DriversPage.searchField.getValue() === '');
        assert.isTrue(!DriversPage.getRowInTable().fullName.getText().includes(driverName));
    });
});
