const UserRoles = require('../../page/UserRoles');

describe('Управление доступом: Добавить новую роль', () => {
    const roleName = `GLHF${Math.random()}`;
    let rolePosition;

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
    });

    it('Нажать многоточие и выбрать "добавить роль"', () => {
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuAddButton.click();
    });

    it('Ввести имя роли, нажать крестик, повторить и сохранить', () => {
        UserRoles.editRoleInput.click();
        UserRoles.editRoleInput.addValue(roleName);
        UserRoles.editRoleClearButton.click();

        UserRoles.editRoleInput.click();
        UserRoles.editRoleInput.addValue(roleName);
        expect(UserRoles.editRoleInput).toHaveAttributeEqual('value', roleName);
        UserRoles.editRoleSaveButton.click();
        UserRoles.alertText.waitForDisplayed();
        expect(UserRoles.alertText).toHaveTextEqual('Успешно сохранено');
    });

    it('Найти созданную роль в списке "Название роли"', () => {
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed();

        expect(UserRoles.allRoles).toHaveTextArrayIncludes(roleName);

        rolePosition = UserRoles.allRoles.findIndex(name => name.getText() === roleName);
    });

    it('Удалить созданную роль', () => {
        UserRoles.roleNumberX(rolePosition).click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
        UserRoles.rolesMenuDeleteButtonYes.click();
    });
});
