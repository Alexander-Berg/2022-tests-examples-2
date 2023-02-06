const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

let user;

describe('Управление доступом: форма редактирования', () => {
    it('Открыть страницу управления доступом', () => {
        user = UserRoles.getRowInTable().email;
        UserRoles.goTo();
        UserRoles.staffTab.click();
        user.waitForDisplayed();
    });

    it('Проверить наличие всех элементов', () => {
        user.moveTo();
        UserRoles.editButton.click();
        assert.isTrue(UserRoles.saveButton.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.closeButton.isDisplayed());
        assert.equal(UserRoles.sideMenu.nameInHeader.getText(), UserRoles.sideMenu.name.getValue());
        assert.isTrue(Boolean(UserRoles.sideMenu.activityCheckbox.getValue()));
        assert.isTrue(UserRoles.sideMenu.phone.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.role.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.name.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.email.getProperty('disabled'));
    });
});
