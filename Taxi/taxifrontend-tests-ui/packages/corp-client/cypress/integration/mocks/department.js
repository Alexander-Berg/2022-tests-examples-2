import deptData from '../../fixtures/responses/department/all-departments.json';

describe('Подразделения', () => {
    const corpUser = 'autotestcorp';

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('/staff');

        cy.intercept('POST', '/api/1.0/search/departments', {
            fixture: 'responses/department/all-departments.json'
        }).as('allDepartments');

        cy.get('.ControlGroup ', {timeout: 10000}).contains('Подразделение').as('addDepartments');
    });

    it('corptaxi-938: Открытие формы создания подразделения из сайдбара', () => {
        cy.get('.MuiIconButton-label > svg').click();
        cy.get('.MuiList-root > [tabindex="-1"]').contains('Добавить подразделение').click();
        cy.get('.DepartmentForm').should('exist');
    });

    it('corptaxi-940: Открытие формы создания подразделения из шапки', () => {
        cy.get('@addDepartments').click();
        cy.get('.DepartmentForm').should('exist');
    });

    it('corptaxi-942: Форма создания подразделения из подразделения', () => {
        cy.visit(`/staff/departments/${deptData.departments[2]._id}#department/add`);
        cy.get('.DepartmentForm .Select-value-label', {timeout: 10000}).should(
            'contain',
            deptData.departments[2].name
        );
    });

    it('corptaxi-536: Добавление подразделения. Вкладка Сотрудники', () => {
        const departmentName = 'manual department';

        cy.intercept('POST', '/api/1.0/client/*/department', {
            _id: '123456789'
        }).as('saveDepartments');

        cy.get('@addDepartments').click();
        cy.get('[name="department.name"]').type(departmentName);
        cy.get('[type="submit"]').click();

        cy.wait('@saveDepartments')
            .its('request.body')
            .then(xhr => {
                expect(xhr).to.deep.equal({
                    counters: {users: 0},
                    name: departmentName,
                    parent_id: null
                });
            });

        cy.xpath(`//*[contains(text(), '${departmentName}')]`).should('exist');
    });

    it('corptaxi-949: Удаление подразделения', () => {
        cy.intercept(
            'DELETE',
            `/api/1.0/client/*/department/${deptData.departments[1]._id}`,
            {
                body: {}
            }
        ).as('deleteDepartments');

        cy.get(`[href="/staff/departments/${deptData.departments[1]._id}"] > div`).as(
            'departmentItem'
        );
        cy.get('@departmentItem').nhover();
        cy.get(
            `[href="/staff/departments/${deptData.departments[1]._id}"] > div > div > button:last-child`
        ).click();
        cy.get('.EditorModalFooterSection__remove').click();
        cy.get('.ConfirmModalFooter__ok').click();

        cy.wait('@deleteDepartments', {timeout: 10000})
            .its('request.url')
            .then(xhr => {
                expect(xhr).contains(
                    `${deptData.departments[1]._id}`
                );
            });

        cy.xpath(`//div[contains(text(),'${deptData.departments[1].name}')]`).should('not.exist');
    });

    context('Проверки корректности работы модалки создания подразделения', () => {
        const MANAGERS_DATA = {
            name: 'Some Manager Name',
            login: 'some_login',
            email: 'some@email.com',
            role: 'Менеджер подразделения{enter}',
            phone: '+790002002020'
        };
        const registerManagerFieldsAliases = () => {
            Object.keys(MANAGERS_DATA).forEach(key => cy.get(`.ManagerFields__${key}`).as(key));
        };
        beforeEach(() => {
            cy.get('div.MuiGrid-container.MuiGrid-align-items-xs-center > div:last-child', {
                timeout: 10000
            }).click();
            cy.get(
                'li.MuiButtonBase-root.MuiListItem-root.MuiMenuItem-root.MuiMenuItem-gutters.MuiListItem-gutters.MuiListItem-button:last-child'
            ).click();
            cy.get('.DepartmentForm').as('departmentForm');
            cy.get('.EditorModalFooterSection__accept').as('acceptButton');
            cy.get('.Managers__add-role-button').as('addRoleButton');
        });

        it('corptaxi-972: Ошибка при создании подразделения с таким же именем', () => {
            cy.intercept('/api/1.0/client/*/department', {
                statusCode: 409,
                body: {
                    code: 'REQUEST_VALIDATION_ERROR',
                    errors: [
                        {
                            text: 'Подразделение с таким именем уже существует',
                            code: 'DUPLICATE_DEPARTMENT_NAME'
                        }
                    ],
                    message: 'Invalid input'
                }
            }).as('createDepartment');

            cy.get('.DepartmentForm__name:first-child').type('Some Name');
            cy.get('.DepartmentForm__parent').type('p{enter}');
            cy.get('@acceptButton').click();
            cy.wait('@createDepartment');

            cy.get('.amber-alert').contains('409: Подразделение с таким именем уже существует');
        });

        it('corptaxi-974: Существующий пользователь роли. Форма роли.', () => {

            cy.server();
            cy.route({
                method: 'POST',
                url: '/api/1.0/client/*/department',
                status: 200,
                delay: 300,
                response: {_id: '77dba69658204e93865bf7078cc3c130'}
            }).as('departments');
            cy.route({
                method: 'POST',
                url: '/api/1.0/client/*/department_manager',
                status: 400,
                response: {
                    "errors": [{
                        "text": "Пользователь с таким логином уже существует",
                        "code": "DUPLICATE_UID"
                    }],
                    "message": "Invalid input",
                    "code": "REQUEST_VALIDATION_ERROR",
                    "details": {
                        "fields": [{
                            "message": "Пользователь с таким логином уже существует",
                            "code": "DUPLICATE_UID",
                            "path": ["yandex_login"]
                        }]
                    }
                }
            }).as('departmentsManager');

            cy.get('.DepartmentForm__name:first-child').type('Some Name');
            cy.get('.DepartmentForm__parent').type('p{enter}');
            cy.get('@addRoleButton').click();
            registerManagerFieldsAliases();

            cy.get('@name').type('Some Manager Name');
            cy.get('@login').type('some_login');
            cy.get('@email').type('some@email.com');
            cy.get('@role').type('Менеджер подразделения{enter}');
            cy.get('@phone').type('+790002002020');

            cy.get('@acceptButton').click();

            cy.wait('@departments');

            cy.get('@departmentForm').find('.SubmittedOverlay').should('exist');

            cy.get('@login').assertFieldError(
                'Пользователь с таким логином в Яндексе уже зарегистрирован'
            );
        });

        it('corptaxi-975: Проверка валидации полей. Форма роли', () => {
            cy.get('@addRoleButton').click();
            cy.get('@acceptButton').click();

            // Регистрируем алиасы менеджерских полей
            registerManagerFieldsAliases();

            // Сперва провяем все required поля
            const managersFieldsKeys = Object.keys(MANAGERS_DATA);
            const requiredFields = [
                '.DepartmentForm__name',
                ...managersFieldsKeys.map(key => `@${key}`)
            ];
            requiredFields.forEach(selector => cy.get(selector).assertFieldInvalid());

            cy.get('.DepartmentForm__name:first-child').type('Some Name');
            cy.get('.DepartmentForm__parent').type('p{enter}');

            const FIELD_TEST_DATA = [
                {
                    key: 'email',
                    error: 'Укажите верный Email!'
                },
                {
                    key: 'phone',
                    error: 'Укажите корректный номер телефона'
                },
                {
                    key: 'role',
                    error: 'Обязательное поле',
                    invalidValue: '123{enter}'
                }
            ];

            FIELD_TEST_DATA.forEach(({key, error, invalidValue = '123'}) => {
                const alias = `@${key}`;
                cy.get(alias).find('input').type(invalidValue);

                cy.get(alias).assertFieldError(error);

                cy.get(alias).find('input').clear().type(MANAGERS_DATA[key]);

                cy.get(alias).assertFieldValid();
            });
        });
    })
});
