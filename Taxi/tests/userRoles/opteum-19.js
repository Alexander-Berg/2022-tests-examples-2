const UserRoles = require('../../page/UserRoles');

describe('Управление доступом: роль без активных пользователей', () => {
    const greyColor = 'rgba(158,155,152,1)';

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.staffTab.click();
        UserRoles.getRowInTable().name.waitForDisplayed();
    });

    it('Деактивировать юзеров у роли opt19', () => {
        const rolesWithUsers = $$('[class*=UsersPage] [class*=UsersContent_wrapper] >div');
        const opt19 = rolesWithUsers.find(el => el.$('span').getText() === 'opteum19');

        const rows = opt19.$$('tr');

        for (const row of rows) {
            row.scrollIntoView();
            row.moveTo();
            UserRoles.editButton.click();

            if (UserRoles.sideMenu.activityCheckbox.getValue('value') === 'true') {
                UserRoles.sideMenu.activityCheckbox.click();
                UserRoles.sideMenu.saveButton.click();
                UserRoles.alert.waitForDisplayed();
            }

            UserRoles.sideMenu.closeButton.click();
        }

    });

    it('Роль opteum19 неактивна, при ховере отображается подсказка', () => {
        const elem = $$('[class*=ScrollListItem] span').find(el => el.getText() === 'opteum19');
        elem.scrollIntoView();
        expect(elem).toHavePropertyEqual('color', greyColor);
        elem.scrollIntoView({block: 'center'});
        elem.moveTo();
        browser.pause(2000);
        expect($('.Tooltip_visible .Tooltip-Content')).toHaveTextEqual('Нет сотрудников с такой ролью');
    });

});
