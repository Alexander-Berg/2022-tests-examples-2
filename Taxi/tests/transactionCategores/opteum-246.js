const TransactionCategoriesPage = require('../../page/TransactionCategoriesPage');
const {assert} = require('chai');

describe('Сортировка категорий транзакции,', () => {
    it('открыт раздел "Категории транзакций"', () => {
        TransactionCategoriesPage.goTo();
    });

    let sorted;

    it('отсортировать по возрастанию', () => {
        TransactionCategoriesPage.sortIcon.click();
        const kategories = $$('tbody td').map(el => el.getText());
        sorted = [...kategories];

        assert.deepEqual(sorted.sort((a, b) => {
            if (a.firstname < b.firstname) {
                return -1;
            }

            if (a.firstname > b.firstname) {
                return 1;
            }

            return 0;
        }), kategories);
    });

    it('отсортировать по убыванию', () => {
        TransactionCategoriesPage.sortIcon.click();
        browser.pause(1000);
        const kategories = $$('tbody td').map(el => el.getText());
        assert.deepEqual(sorted.reverse(), kategories);
    });

});
