import EmployeesPage from '../../../PageObjects/EmployeesPage';

describe('Раздел Сотрудники', () => {
    const corpUser = 'autotestcorp-newVersion';
    const staff = new EmployeesPage();

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('/v2/staff');

        cy.intercept('POST', '/api/1.0/search/departments', {
            fixture: 'responses/search/departments.json'
        });
        cy.intercept('POST', '/api/2.0/users', {id: '123'}).as('saveUser');
        cy.intercept('PUT', '/api/2.0/users/*', {}).as('saveEditedUser');
        cy.intercept('GET', '/api/2.0/users*', {fixture: 'responses/2.0/users/users.json'});
        cy.intercept('GET', '/api/2.0/users/a59993fba4e44b2db190f2f4d95e081e', {
            fixture: 'responses/2.0/users/user.json'
        });
    });

    const USER = {
        name: 'Вадим Юзер',
        phone: '+79435634722',
        email: 'vadim3214@yanzddex.ru',
        id: '12'
    };

    it('corptaxi-1087: Добавление нового сотрудника. Новые лимиты. Вкладка Сотрудники', () => {
        staff.fillEmployeeFields(USER).clickBtn('Сохранить');

        cy.wait('@saveUser')
            .its('request.body')
            .then(body => {
                expect(body.fullname).eq(USER.name);
                expect(body.phone).eq(USER.phone);
                expect(body.nickname).eq(USER.id);
                expect(body.email).eq(USER.email);
            });
    });

    it('corptaxi-886: Редактирование сотрудника. Вкладка Сотрудники', () => {
        staff.openEmployee('Вадим Юзер').typeEmail('editemail@sobak.kek').clickBtn('Сохранить');

        cy.wait('@saveEditedUser')
            .its('request.body')
            .then(body => {
                expect(body.email).eq('editemail@sobak.kek');
            });
    });

    it('corptaxi-885: Удаление сотрудника. Вкладка Сотрудники', () => {
        staff.openEmployee('Вадим Юзер').clickDeleteBtn().clickBtn('Удалить');

        cy.wait('@saveEditedUser')
            .its('request.body')
            .then(body => {
                expect(body.is_deleted).eq(true);
            });
    });

    it('corptaxi-406: Восстановление удаленного сотрудника. Вкладка Сотрудники', () => {
        cy.intercept('GET', '/api/2.0/users*search*', {
            fixture: 'responses/2.0/users/users-with-deleted.json'
        });
        cy.intercept('GET', '/api/2.0/users/a59993fba4e44b2db190f2f4d95e081e', {
            fixture: 'responses/2.0/users/user-deleted.json'
        });

        staff
            .searchEmployee('+79435634722')
            .openEmployee('Вадим Удаленный', true)
            .clickRestoreBtn();

        cy.wait('@saveEditedUser')
            .its('request.body')
            .then(body => {
                expect(body.is_deleted).eq(undefined);
                expect(body.is_active).eq(true);
            });
    });

    it('corptaxi-884: Просмотр истории использования сервисов сотрудником. Вкладка Сотрудники', () => {
        staff.openEmployee('Вадим Юзер');
        // сайпрес не умеет работать с новой вкладкой, проверяется href и просто клик по кнопке
        cy.xpath('//a[@href="/orders?user_id=a59993fba4e44b2db190f2f4d95e081e"]').should('exist');
        staff.openOrderHistory();
    });

    it('corptaxi-876: Создание сотрудника сразу в подразделение. Вкладка Сотрудники', () => {
        staff.fillEmployeeFields(USER).selectDepartment('test').clickBtn('Сохранить');

        cy.wait('@saveUser')
            .its('request.body')
            .then(body => {
                expect(body.fullname).eq(USER.name);
                expect(body.phone).eq(USER.phone);
                expect(body.nickname).eq(USER.id);
                expect(body.email).eq(USER.email);
                expect(body.department_id).eq('5b6177aca60946709d6d55d8357c7b7f');
            });
    });
});
