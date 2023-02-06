const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Добавить существующую роль', () => {
    const roleName = 'GLHF';

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
    });

    it('Нажать многоточие и выбрать "добавить роль"', () => {
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuAddButton.click();
    });

    it('Ввести имя роли и сохранить', () => {
        UserRoles.type(UserRoles.editRoleInput, roleName);
        assert.equal(UserRoles.editRoleInput.getValue(), roleName);
        UserRoles.editRoleSaveButton.click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Такая роль уже существует');
    });

    it('Убедиться что роль в 1 экземпляре', () => {
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed();
        let roleCount = 0;

        UserRoles.allRoles.forEach(name => {
            // !FIXME: заиспользовать строгое ===
            // eslint-disable-next-line eqeqeq
            if (name.getText() == roleName) {
                roleCount += 1;
            }
        });

        assert.equal(roleCount, 1);
    });
});
