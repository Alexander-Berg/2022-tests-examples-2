const DriversPage = require('../../page/DriversPage');
const {assert} = require('chai');

let listLength;

describe('Поиск водителя по имени', () => {
    it('Открыть страницу водителей', () => {
        DriversPage.goTo();
    });

    it('В строке поиска указать ФИО водителя "Рулон"', () => {
        DriversPage.searchField.waitForDisplayed({timeout: 5000});
        DriversPage.type(DriversPage.searchField, 'Рулон');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.equal(listLength, 1);
        assert.equal(DriversPage.getRowInTable(1).fullName.getText().replace(/\s/g, ''), 'ОбоевРулонСмотан');
    });

    it('Указать ФИО водителя "Иван"', () => {
        DriversPage.clearWithBackspace(DriversPage.searchField);
        DriversPage.type(DriversPage.searchField, 'иван');
        browser.pause(2000);
        listLength = $$('table tbody >tr').length;

        assert.isTrue(listLength > 1);

        // ФИО водителей содержит введенную в поиске часть
        DriversPage.goThroughPaginations(
            rows => {
                for (let i = 0; i < rows.length - 1; i++) {
                    assert.isTrue(rows[i].getText().toLowerCase().includes('иван'));
                }

                return false;
            },
            4,
            2000,
        );
    });
});
