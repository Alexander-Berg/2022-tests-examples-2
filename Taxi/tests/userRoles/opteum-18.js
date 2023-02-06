const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: сортировка ролей', () => {
    const opteum18 = 'opteum18';
    const temporaryRole = 'temporaryRole';
    let opteum18PositionNumber, temporaryRolePositionNumber;

    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.staffTab.click();
        UserRoles.getRowInTable().name.waitForDisplayed();
    });

    it('Оставить одного активного сотрудника в роли "opteum18", всем остальным активным сменить роль на "temporaryRole"', () => {
        UserRoles.moveAllUsersFromRole(opteum18, temporaryRole, 1);
    });

    it('Роль "temporaryRole" переместилась вниз', () => {
        opteum18PositionNumber = UserRoles.findRoleNumberByName(opteum18);
        temporaryRolePositionNumber = UserRoles.findRoleNumberByName(temporaryRole);
        assert.isTrue(opteum18PositionNumber > temporaryRolePositionNumber);
        assert.isTrue(UserRoles.countElementsInRole(opteum18PositionNumber) < UserRoles.countElementsInRole(temporaryRolePositionNumber));
    });

    it('Сменить сотрудникам роль "temporaryRole" на роль "opteum18", оставив одного активного сотрудника в роли "temporaryRole', () => {
        UserRoles.moveAllUsersFromRole(temporaryRole, opteum18, 1);
    });

    it('Роль "temporaryRole" переместилась вверх', () => {
        opteum18PositionNumber = UserRoles.findRoleNumberByName(opteum18);
        temporaryRolePositionNumber = UserRoles.findRoleNumberByName(temporaryRole);
        assert.isTrue(opteum18PositionNumber < temporaryRolePositionNumber);
        assert.isTrue(UserRoles.countElementsInRole(opteum18PositionNumber) > UserRoles.countElementsInRole(temporaryRolePositionNumber));
    });
});
