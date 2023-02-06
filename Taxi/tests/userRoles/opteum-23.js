const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Изменение доступа роли без подтверждения', () => {

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.rolesTab.click();
        UserRoles.roleNumberX().waitForDisplayed();
    });

    it('Выбрать редактируемую роль', () => {
        UserRoles.roleNumberX().click();
    });

    it('Выбрать раздел "Автопарк"', () => {
        UserRoles.permissionSections[1].click();
        UserRoles.checkbox[0].waitForDisplayed();
    });

    it('Выставить галку чекбоксу "автомобили" если она убрага', () => {
        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (UserRoles.checkboxAttribute[0].isSelected() == false) {
            UserRoles.checkbox[0].click();
            UserRoles.alertText.waitForDisplayed();
            assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
            browser.refresh();
            UserRoles.roleNumberX().waitForDisplayed();
        }
    });

    it('Убрать галку "Автомобили"', () => {
        UserRoles.checkbox[0].click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
        assert.isFalse(UserRoles.checkboxAttribute[0].isSelected());
        assert.equal(UserRoles.checkboxSubtitle[0].getText(), 'Нет доступа к разделу');
        assert.equal(UserRoles.checkboxTitle[1].getText(), 'Периодические списания');
    });

    it('Поставить галку у пункта "Автомобиль"', () => {
        browser.refresh();
        UserRoles.roleNumberX().waitForDisplayed();
        UserRoles.checkbox[0].click();
        UserRoles.alertText.waitForDisplayed();
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
        assert.isTrue(UserRoles.checkboxAttribute[0].isSelected());
        assert.equal(UserRoles.checkboxSubtitle[0].getText(), 'Есть доступ к разделу');
        assert.equal(UserRoles.checkboxTitle[1].getText(), 'Создание и редактирование');
        assert.equal(UserRoles.checkboxTitle[2].getText(), 'Выгрузка в файл');
    });
});
