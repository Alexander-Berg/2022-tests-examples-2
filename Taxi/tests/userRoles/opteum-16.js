const UserRoles = require('../../page/UserRoles');
const {assert} = require('chai');

describe('Управление доступом: фильтры', () => {
    it('Открыть страницу управления доступом', () => {
        UserRoles.goTo();
        UserRoles.staffTab.click();
    });

    it('Выбрать фильтр "Неактивеные"', () => {
        UserRoles.filterInactive.click();
        UserRoles.getRowInTable().status.waitForDisplayed();

        UserRoles.allStatuses.forEach(status => {
            assert.equal(status.getText(), 'Неактивен');
        });
    });

    it('Выбрать фильтр "Активные"', () => {
        UserRoles.filterActive.click();
        UserRoles.getRowInTable().status.waitForDisplayed();

        UserRoles.allStatuses.forEach(status => {
            assert.equal(status.getText(), 'Активен');
        });
    });
});
