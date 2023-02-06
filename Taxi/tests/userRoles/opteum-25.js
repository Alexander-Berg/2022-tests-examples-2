const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Нельзя редактировать роль директора', () => {

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
    });

    it('Выбрать директора', () => {
        UserRoles.directorRole.click();
        UserRoles.checkbox[0].waitForDisplayed();
    });

    it('Убрать галку "Водители"', () => {
        UserRoles.checkbox[0].click();
        assert.isTrue(UserRoles.checkboxAttribute[0].getProperty('disabled'));
        assert.isTrue(UserRoles.checkboxAttribute[0].getProperty('checked'));
    });
});
