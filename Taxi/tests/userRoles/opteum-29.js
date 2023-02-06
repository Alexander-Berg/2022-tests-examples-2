const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Удалить пустую роль', () => {
    const roleName = `GLHF${Math.random()}`;
    let role;

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
    });

    it('Добавить роль', () => {
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuAddButton.click();
        UserRoles.type(UserRoles.editRoleInput, roleName);
        assert.equal(UserRoles.editRoleInput.getValue(), roleName);
        UserRoles.editRoleSaveButton.click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Успешно сохранено');
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed();

        UserRoles.allRoles.forEach(name => {
            // !FIXME: заиспользовать строгое ===
            // eslint-disable-next-line eqeqeq
            if (name.getText() == roleName) {
                role = name;
            }
        });
    });

    it('Нажать удалить, нажать "Нет"', () => {
        role.click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
        UserRoles.rolesMenuDeleteButtonNo.click();
        assert.isTrue(role.waitForDisplayed());
    });

    it('Повторить, нажать "Да"', () => {
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
        UserRoles.rolesMenuDeleteButtonYes.click();
        assert.equal(UserRoles.alertText.getText(), 'Роль успешно удалена');
        let roleExist = false;

        UserRoles.allRoles.forEach(name => {
            // !FIXME: заиспользовать строгое ===
            // eslint-disable-next-line eqeqeq
            if (name.getText() == roleName) {
                roleExist = true;
            }
        });

        assert.isFalse(roleExist);
    });
});
