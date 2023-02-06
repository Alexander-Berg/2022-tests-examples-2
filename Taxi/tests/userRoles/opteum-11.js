const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Создание сотрудника: негатив', () => {
    const randomString = Math.random().toString();
    const role = 'Администратор';
    const email = 'abcd@yandex.ru';

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.staffTab.click();
        UserRoles.roleNumberX().waitForDisplayed({timeout: 2000});
    });

    it('нажать кнопку "+"', () => {
        UserRoles.addNewUserButton.click();
    });

    it('В пустой форме нажать кнопку "Сохранить"', () => {
        UserRoles.saveButton.click();
        UserRoles.saveButton.waitForDisplayed({timeout: 2000});
        // цвет обводки у полей "Роль", "ФИО", "Email" стал красным
        assert.isTrue(UserRoles.sideMenu.roleError.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.textInputError[0].isDisplayed());
        assert.isTrue(UserRoles.sideMenu.textInputError[1].isDisplayed());
        // под полями "Роль", "ФИО", "Email" появилась надпись "Это поле необходимо заполнить" красного цвета
        assert.isTrue(UserRoles.sideMenu.roleErrorHint.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.nameErrorHint.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.emailErrorHint.isDisplayed());
    });

    it('Заполнить поле "Телефон" Нажать кнопку "Сохранить"', () => {
        UserRoles.sideMenu.phone.setValue(randomString);
        UserRoles.saveButton.waitForDisplayed({timeout: 2000});
        UserRoles.saveButton.click();
        // информаци о необходимости заполнения обязательных полей остается
        assert.isTrue(UserRoles.sideMenu.roleErrorHint.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.nameErrorHint.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.emailErrorHint.isDisplayed());
    });

    it('Выбрать любую роль из списка Нажать кнопку "Сохранить"', () => {
        UserRoles.sideMenu.phone.waitForDisplayed({timeout: 2000});
        UserRoles.sideMenu.role.click();
        browser.pause(250);
        UserRoles.sideMenu.roleInput.setValue(role);
        browser.keys('Enter');
        UserRoles.saveButton.click();
        // поле "Роль" отображает выбранное значение
        assert.equal(UserRoles.sideMenu.roleInputContent.getText(), role);
        // поле "Роль" больше не отмечено как незаполненное
        assert.isFalse(UserRoles.sideMenu.roleError.isDisplayed());
        // информаци о необходимости заполнения обязательных полей остается
        assert.isFalse(UserRoles.sideMenu.roleErrorHint.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.nameErrorHint.isDisplayed());
        assert.isTrue(UserRoles.sideMenu.emailErrorHint.isDisplayed());
    });

    it('Отображается ошибка при незаполненном поле Email', () => {
        UserRoles.sideMenu.name.waitForDisplayed({timeout: 2000});
        UserRoles.sideMenu.name.click();
        UserRoles.sideMenu.name.setValue(randomString);
        UserRoles.saveButton.click();
        // поле "ФИО" отображает введенное значение
        assert.equal(UserRoles.sideMenu.name.getValue(), randomString);
        // поле "ФИО" больше не отмечено как незаполненное
        assert.isFalse(UserRoles.sideMenu.nameErrorHint.isDisplayed());
        // информаци о необходимости заполнения обязательных полей остается
        assert.isTrue(UserRoles.sideMenu.emailErrorHint.isDisplayed());
    });

    it('Отображается ошибка при незаполненном поле ФИО', () => {
        UserRoles.sideMenu.name.waitForDisplayed({timeout: 2000});
        UserRoles.sideMenu.name.click();
        UserRoles.clearWithBackspace(UserRoles.sideMenu.name);
        UserRoles.sideMenu.email.click();
        UserRoles.sideMenu.email.setValue(email);
        UserRoles.saveButton.click();
        browser.pause(300);
        // поле "Email" отображает введенное значение
        assert.equal(UserRoles.sideMenu.email.getValue(), email);
        // поле "Email" больше не отмечено как незаполненное
        assert.isFalse(UserRoles.sideMenu.emailErrorHint.isDisplayed());
        // информаци о необходимости заполнения обязательных полей остается
        assert.isTrue(UserRoles.sideMenu.nameErrorHint.isDisplayed());
    });
});
