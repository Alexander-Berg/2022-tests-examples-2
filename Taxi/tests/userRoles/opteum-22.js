const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Редактирование роли: название', () => {
    const roleName = 'Администратор';
    const testName = 'opt22test';

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
    });

    it('Проверка наличия тестовых данных', () => {
        UserRoles.staffTab.click();
        UserRoles.getRowInTable().name.waitForDisplayed();
        const testRoleNumber = UserRoles.findRoleNumberByName(testName);

        if (testRoleNumber) {
            UserRoles.rolesTab.click();
            UserRoles.roleNumberX(testRoleNumber, true).scrollIntoView({block: 'center'});
            UserRoles.roleNumberX(testRoleNumber, true).click();
            UserRoles.rolesMenu.click();
            UserRoles.rolesMenuEditButton.click();
            UserRoles.clearWithBackspace(UserRoles.editRoleInput);
            UserRoles.editRoleInput.click();
            UserRoles.editRoleInput.addValue(roleName);
            UserRoles.editRoleSaveButton.click();
            UserRoles.alertText.waitForDisplayed();
            browser.refresh();
            UserRoles.roleNumberX().waitForDisplayed();
        }
    });

    it('выбрать роль, нажать многоточие и выбрать "редактировать роль"', () => {
        UserRoles.rolesTab.click();
        UserRoles.roleNumberX().waitForDisplayed();
        UserRoles.roleNumberX().click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuEditButton.click();
        assert.equal(UserRoles.editRoleInput.getValue(), roleName);
    });

    it('Изменяем название и нажать кнопку "Готово"', () => {
        UserRoles.clearWithBackspace(UserRoles.editRoleInput);
        UserRoles.editRoleInput.click();
        UserRoles.editRoleInput.addValue(testName);
        UserRoles.editRoleSaveButton.click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Успешно сохранено');
        assert.notEqual(roleName, UserRoles.roleNumberX().getText());
    });

    it('Переименовать роль обратно', () => {
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed();
        UserRoles.roleNumberX().click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuEditButton.click();
        UserRoles.clearWithBackspace(UserRoles.editRoleInput);
        UserRoles.editRoleInput.click();
        UserRoles.editRoleInput.addValue(roleName);
        UserRoles.editRoleSaveButton.click();
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed();
        assert.equal(roleName, UserRoles.roleNumberX().getText());
    });
});
