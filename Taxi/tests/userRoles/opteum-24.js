const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Изменение доступа роли с подтверждением', () => {
    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
        UserRoles.roleNumberX().waitForDisplayed({timeout: 100_000});
    });

    it('выбрать  редактируемую роль', () => {
        UserRoles.roleNumberX().click();
    });

    it('Выбрать раздел "Водители"', () => {
        UserRoles.permissionSections[0].click();
        UserRoles.checkbox[2].waitForDisplayed({timeout: 100_000});
    });

    it('Выставить галку чекбоксу "Списание с баланса водителя" если она убрана', () => {
        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (UserRoles.checkboxAttribute[2].getProperty('checked') == false) {
            UserRoles.checkbox[2].click();
            UserRoles.saveButton.click();
            browser.refresh();
            UserRoles.roleNumberX().waitForDisplayed({timeout: 100_000});
        }
    });

    it('Убрать галку "Списание с баланса водителя"', () => {
        UserRoles.checkbox[2].click();
    });

    it('Нажать кнопку "Отмена"', () => {
        UserRoles.cancelButton.click();
        assert.isTrue(UserRoles.checkboxAttribute[2].getProperty('checked'));
    });

    it('Повторить и нажать "сохранить"', () => {
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed({timeout: 100_000});
        UserRoles.checkbox[2].click();
        UserRoles.saveButton.click();
        UserRoles.alertText.waitForDisplayed({timeout: 100_000});
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
        assert.isFalse(UserRoles.checkboxAttribute[2].getProperty('checked'));
    });

    it('Включить обратно', () => {
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed({timeout: 100_000});
        UserRoles.checkbox[2].click();
        UserRoles.saveButton.click();
        UserRoles.alertText.waitForDisplayed({timeout: 100_000});
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
        assert.isTrue(UserRoles.checkboxAttribute[2].getProperty('checked'));
    });
});
