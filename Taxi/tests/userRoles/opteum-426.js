const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: Отображение пустой роли', () => {

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
    });

    it('Роль opteum-426 неактивна, при ховере отображается подсказка', () => {
        const elem = $('span=opteum-426');
        elem.waitForDisplayed();
        elem.scrollIntoView({block: 'center'});
        elem.moveTo();
        $('.Tooltip_visible').waitForDisplayed();
        assert.equal($('.Tooltip_visible .Tooltip-Content').getText(), 'Нет сотрудников с такой ролью');
    });

    it('роль не отображается в списке сотрудников', () => {
        const rolesWithUsers = $$('[class*=UsersPage] [class*=UsersContent_wrapper] >div >div:first-child span');

        rolesWithUsers.forEach(el => {
            assert.notEqual(el.getText(), 'opteum-426');
        });

    });

});
