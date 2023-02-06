const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Нельзя удалить роль директора', () => {

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
    });

    it('Выбрать директора и нажать удалить', () => {
        UserRoles.directorRole.click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
    });

    it('Нажать "нет"', () => {
        UserRoles.rolesMenuDeleteButtonNo.click();
        assert.isTrue(UserRoles.directorRole.waitForDisplayed());
    });

    it('Повторить и нажать "да"', () => {
        UserRoles.directorRole.click();
        UserRoles.rolesMenu.click();
        UserRoles.rolesMenuDeleteButton.click();
        UserRoles.rolesMenuDeleteButtonYes.click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Данная роль не может быть удалена');
        assert.isTrue(UserRoles.directorRole.waitForDisplayed());
    });
});
