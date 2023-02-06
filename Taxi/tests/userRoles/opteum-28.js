const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Нельзя удалить непустую роль', () => {
    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
    });

    it('Выбрать непустую роль и нажать удалить', () => {
        UserRoles.roleNumberX().click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
    });

    it('Нажать "нет"', () => {
        UserRoles.rolesMenuDeleteButtonNo.click();
        assert.isTrue(UserRoles.roleNumberX().waitForDisplayed());
    });

    it('Повторить и нажать "да"', () => {
        UserRoles.roleNumberX().click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
        UserRoles.rolesMenuDeleteButtonYes.click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Роль должна быть пустой');
        assert.isTrue(UserRoles.roleNumberX().waitForDisplayed());
    });
});
