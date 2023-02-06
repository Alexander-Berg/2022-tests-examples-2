const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

let listLength;

describe('Поиск водителя по номеру автомобиля', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('В строке поиска, справа от заголовка, указать номер автомобиля водителя "Y002KX799"', () => {
        DriversPage.searchField.waitForDisplayed({timeout: 5000});
        DriversPage.type(DriversPage.searchField, 'Y002KX799');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.equal(listLength, 1);
        assert.isTrue(DriversPage.getRowInTable(1).vehicle.getText().includes('Y002KX799'));
        assert.equal(DriversPage.getRowInTable(1).fullName.getText().replace(/\s/g, ''), 'ttinattina');
    });

    it('Указать номер автомобиля "TT003"', () => {
        DriversPage.clearWithBackspace(DriversPage.searchField);
        DriversPage.type(DriversPage.searchField, 'TT003');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.isTrue(listLength > 1);

        for (let i = 1; i <= listLength; i++) {
            assert.isTrue(DriversPage.getRowInTable(i).vehicle.getText().includes('TT003'));
        }
    });
});
