const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

let listLength;

describe('Поиск водителя по ВУ', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('В строке поиска указать водительское удостоверение (ВУ) водителя "4507333333"', () => {
        DriversPage.searchField.waitForDisplayed({timeout: 5000});
        DriversPage.type(DriversPage.searchField, '4507333333');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.equal(listLength, 1);
        assert.equal(DriversPage.getRowInTable(1).fullName.getText().replace(/\s/g, ''), 'ОбоевРулонСмотан');
    });

    it('В строке поиска указать водительское удостоверение (ВУ) водителя "4507"', () => {
        DriversPage.clearWithBackspace(DriversPage.searchField);
        DriversPage.type(DriversPage.searchField, '4507');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.isTrue(listLength > 1);

        for (let i = 1; i <= listLength; i++) {
            assert.isTrue(DriversPage.getRowInTable(i).driverLicense.getText().includes('4507'));
        }
    });
});
