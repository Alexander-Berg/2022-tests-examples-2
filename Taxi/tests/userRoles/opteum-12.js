const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: редактирование сотрудника', () => {
    let userName, userPhone, userRole, userRowSelector;
    const userEmail = 'testpartners@yandex.ru';
    const randomInt = Math.floor(Math.random() * (999_999 - 100_000) + 100_000);
    const randomString = randomInt.toString();
    let newRole = 'НеДиректор';

    it('Открыть страницу управления доступом и дождать прогрузки', () => {
        userRowSelector = UserRoles.getRowInTable().name;
        UserRoles.goTo();
        UserRoles.staffTab.click();
        userRowSelector.waitForDisplayed({timeout: 15_000});
    });

    it('Найти пользователя', () => {
        UserRoles.search.setValue(userEmail);
        browser.pause(1000);
    });

    it('Открыть сайдменю редактирования', () => {
        userRowSelector.moveTo();
        UserRoles.editButton.click();
        browser.pause(500);
    });

    it('Сохранить изначальные данные', () => {
        userPhone = UserRoles.sideMenu.phone.getValue();
        userName = UserRoles.sideMenu.name.getValue();
        userRole = UserRoles.sideMenu.role.getText();

        // !FIXME: заиспользовать строгое ===
        // eslint-disable-next-line eqeqeq
        if (userRole == newRole) {
            newRole = 'Администратор';
        }
    });

    it('Изменить все поля и сохранить', () => {
        UserRoles.sideMenu.phone.waitForDisplayed({timeout: 15_000});
        UserRoles.sideMenu.phone.click();
        UserRoles.clearWithBackspace(UserRoles.sideMenu.phone);
        UserRoles.sideMenu.phone.setValue(randomString);
        UserRoles.sideMenu.name.click();
        UserRoles.clearWithBackspace(UserRoles.sideMenu.name);
        UserRoles.sideMenu.name.setValue(randomString);
        UserRoles.sideMenu.role.click();
        UserRoles.focusedInput.addValue(newRole);
        browser.keys('Enter');
        UserRoles.saveButton.click();
        UserRoles.alertText.waitForDisplayed({timeout: 15_000});
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
    });

    it('Обновить страницу', () => {
        browser.refresh();
        userRowSelector.waitForDisplayed({timeout: 15_000});
    });

    it('Проверить отображение измененого имени в таблице', () => {
        assert.equal(userRowSelector.getText(), randomString);
    });

    it('Открыть сайдменю редактирования', () => {
        userRowSelector.moveTo();
        UserRoles.editButton.click();
        browser.pause(500);
    });

    it('Проверить соответствие открывшихся данных и тех что мы вводили', () => {
        assert.equal(UserRoles.sideMenu.phone.getValue(), randomString);
        assert.equal(UserRoles.sideMenu.role.getText(), newRole);
        assert.equal(UserRoles.sideMenu.name.getValue(), randomString);
    });

    it('Вернуть данные к начальному состоянию', () => {
        UserRoles.sideMenu.phone.click();
        UserRoles.clearWithBackspace(UserRoles.sideMenu.phone);
        UserRoles.sideMenu.phone.setValue(userPhone);
        UserRoles.sideMenu.name.click();
        UserRoles.clearWithBackspace(UserRoles.sideMenu.name);
        UserRoles.sideMenu.name.setValue(userName);
        UserRoles.sideMenu.role.click();
        UserRoles.focusedInput.addValue(userRole);
        browser.keys('Enter');
        UserRoles.saveButton.click();
        UserRoles.alertText.waitForDisplayed(15_000);
        assert.equal(UserRoles.alertText.getText(), 'Изменение сохранено');
    });
});
