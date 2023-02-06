const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

let listLength;

describe('Поиск водителя по позывному', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('В строке поиска указать позывной водителя "QA000002"', () => {
        DriversPage.searchField.waitForDisplayed({timeout: 5000});
        DriversPage.type(DriversPage.searchField, 'QA000002');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.equal(listLength, 1);
        assert.equal(DriversPage.getRowInTable(1).codeName.getText(), 'QA000002');
        assert.equal(DriversPage.getRowInTable(1).fullName.getText().replace(/\s/g, ''), '123Тест11');
    });

    it('Указать позывной водителя "QA000"', () => {
        DriversPage.clearWithBackspace(DriversPage.searchField);
        DriversPage.type(DriversPage.searchField, 'QA000');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.isTrue(listLength > 1);

        for (let i = 1; i <= listLength; i++) {
            assert.isTrue(DriversPage.getRowInTable(i).codeName.getText().includes('QA000'));
        }
    });
});
