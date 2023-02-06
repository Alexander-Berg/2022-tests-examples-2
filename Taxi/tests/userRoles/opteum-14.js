const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: вкл/выкл сотрудника', () => {
    let email,
        user;

    it('Открыть страницу управления доступом для вкл/выкл сотрудника', () => {
        user = UserRoles.getRowInTable().email;
        UserRoles.goTo();
        UserRoles.staffTab.click();
        user.waitForDisplayed();
    });

    it('Кликнуть по кнопке "редактировать" любому активному сотруднику в списке сотрудников', () => {
        user.moveTo();
        UserRoles.editButton.click();
        email = UserRoles.sideMenu.email.getValue();
    });

    it('Выключить чекбокс "Активность" и нажать кнопку "Сохранить"', () => {
        UserRoles.sideMenu.activityCheckbox.click();

        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (UserRoles.sideMenu.activityCheckbox.getValue() == 'true') {
            UserRoles.sideMenu.activityCheckbox.click();
        }

        UserRoles.saveButton.click();
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');// отобразился тост об успешном сохранении изменений
        browser.refresh();
    });

    it('Найти в списке сотрудников неактивного сотрудника и кликнуть по записи для открытия формы редактирования', () => {
        UserRoles.type(UserRoles.search, email);
        user.waitForDisplayed();
        assert.equal(user.getText(), email); // сотрудник найден
        user.moveTo();
        UserRoles.editButton.click();
        assert.equal(UserRoles.sideMenu.activityCheckbox.getValue(), 'false'); // статус сотрудника "Неактивен"
    });

    it('В открытой карточке активировать сотрудника', () => {
        UserRoles.sideMenu.activityCheckbox.click();
        UserRoles.saveButton.click();
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');// отобразился тост об успешном сохранении изменений
    });

    it('Найти в списке сотрудника и кликнуть по записи для открытия формы редактирования', () => {
        user.moveTo();
        UserRoles.editButton.click();
        assert.equal(UserRoles.sideMenu.activityCheckbox.getValue(), 'true'); // статус "Активен"
    });
});
