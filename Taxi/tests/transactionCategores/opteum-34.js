const TransactionCategoriesPage = require('../../page/TransactionCategoriesPage');
const {assert} = require('chai');

describe('Архивация и активация категории транзакции,', () => {
    it('открыт раздел "Категории транзакций"', () => {
        TransactionCategoriesPage.goTo();
    });

    it('сделать категорию opteum-34 активной', () => {
        TransactionCategoriesPage.archiveButton.moveTo();
        TransactionCategoriesPage.archiveButton.click();

        browser.pause(1000);
        const opteum34 = $$('[class*=Table] td').find(el => el.getText() === 'opteum-34');

        if (opteum34) {
            opteum34.click();
            $('.Checkbox').click();
            $('span=Сохранить').click();
            $('[class*=Alert]').waitForDisplayed();
        }

    });

    it('проверить роль opteum-34 в списке активных', () => {
        TransactionCategoriesPage.activeButton.click();
        browser.pause(1000);
        const activeTransactions = $$('[class*=Table] td').map(el => el.getText());
        assert.isTrue(activeTransactions.includes('opteum-34'));
    });

    it('архивировать роль opteum-34', () => {
        const active = $$('[class*=Table] td').find(el => el.getText() === 'opteum-34');
        active.click();
        $('.Checkbox').click();
        $('span=Сохранить').click();
        $('[class*=Alert]').waitForDisplayed();
    });

    it('проверить роль в архиве', () => {
        $('[class*=Alert]').waitForDisplayed({reverse: true});
        TransactionCategoriesPage.archiveButton.click();
        browser.pause(1000);
        const archive = $$('[class*=Table] td').map(el => el.getText());
        assert.isTrue(archive.includes('opteum-34'));
    });

});
