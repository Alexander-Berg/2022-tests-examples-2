const TransactionCategoriesPage = require('../../page/TransactionCategoriesPage');
const {assert} = require('chai');

describe('Переименовать категорию,', () => {
    it('открыт раздел "Категории транзакций"', () => {
        TransactionCategoriesPage.goTo();
    });

    let categoryNameInput,
        gg,
        opteum320;

    it('Precondition: переименовать gg в opteum-320', () => {
        gg = $('td=gg');

        if (gg.isDisplayed()) {
            gg.moveTo();
            gg.click();
            categoryNameInput = TransactionCategoriesPage.editRoleForm.roleNameInput;
            TransactionCategoriesPage.clearWithBackspace(categoryNameInput);
            TransactionCategoriesPage.type(categoryNameInput, 'opteum-320');
            $('button=Сохранить').click();
            $('[class*=Alert]').waitForDisplayed();
            browser.refresh();
        }

    });

    it('Изменить имя категории opteum-320 на gg', () => {
        opteum320 = $('td=opteum-320');
        opteum320.moveTo();
        opteum320.click();
        categoryNameInput = TransactionCategoriesPage.editRoleForm.roleNameInput;
        TransactionCategoriesPage.clearWithBackspace(categoryNameInput);
        TransactionCategoriesPage.type(categoryNameInput, 'gg');
        $('button=Сохранить').click();
        $('[class*=Alert]').waitForDisplayed();
        browser.refresh();
    });

    it('в списке отсутствует категория opteum-320', () => {
        const names = $$('td').map(el => el.getText());
        assert.equal(names.indexOf('opteum-320'), -1);
    });

    it('переименовать категорию с gg на opteum-320', () => {
        gg = $('td=gg');
        gg.moveTo();
        gg.click();
        categoryNameInput = TransactionCategoriesPage.editRoleForm.roleNameInput;
        TransactionCategoriesPage.clearWithBackspace(categoryNameInput);
        TransactionCategoriesPage.type(categoryNameInput, 'opteum-320');
        $('button=Сохранить').click();
        $('[class*=Alert]').waitForDisplayed();
    });

});
