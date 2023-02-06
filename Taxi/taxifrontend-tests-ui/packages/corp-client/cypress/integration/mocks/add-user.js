const group = require('../../fixtures/responses/group/group.json');
const fixtureUser = require('../../fixtures/responses/search/user/user.json');
const openServicesTab = () => {
    cy.get('@tabs', {timeout: 10000}).contains('Сервисы').click();
    cy.get('.ServicesConfig').as('ServicesConfSection');
};

const openEmployeeTab = () => {
    cy.get('@tabs').contains('Сотрудники').click();
};

context('Модалка редактирования и удаления сотрудника', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();

        cy.corpOpen('/staff');
        cy.intercept('GET', '/api/1.0/client/*/user*', {fixture: 'responses/search/user/user.json'});
        cy.intercept('GET', '/api/1.0/client/*/user/*', fixtureUser.items[0]);
    });

    it('corptaxi-338: Редактирование сотрудника. Вкладка Сотрудники', () => {
        cy.intercept('PUT', 'api/1.0/client/*/user/*', {}).as('saveUser');

        cy.get('.UserV2__fullname').nhover();
        cy.get('.amber-icon_edit').click();
        cy.get('[name="email"]').clear().type('igorNic@gmail.com');
        cy.get('.UserForm').contains('Сохранить').click();

        cy.wait('@saveUser').its('request.body')
            .then(body => {
                expect(body.fullname).eq(fixtureUser.items[0].fullname);
                expect(body.phone).eq(fixtureUser.items[0].phone);
                expect(body.email).eq('igorNic@gmail.com');
                expect(body.nickname).eq(fixtureUser.items[0].nickname);
            });

    });

    it('corptaxi-400: Удаление сотрудника. Вкладка Сотрудники', () => {
        cy.intercept('DELETE', 'api/1.0/client/*/user/*', {}).as('saveUser');

        cy.get('.UserV2__fullname').nhover();
        cy.get('.amber-icon_edit').click();

        cy.xpath('//*[text()="Удалить"]').click();
        cy.xpath('//*[text()="Удалить"]').click();
        cy.xpath('//*[text()="В этой группе ещё нет сотрудников"]').should('be.visible');
    });
});

context('Модалка добавления новых сотрудников', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();
        cy.server();
        // Точно включаем опцию ограничений
        cy.route('/api/1.0/client/*', 'fixture:responses/client/200-with-restrictions').as(
            'client'
        );
        cy.corpOpen('/staff');
        cy.route({
            method: 'GET',
            url: '/api/1.0/client/*/user*',
            response: 'fixture:responses/search/user/empty'
        });
        cy.route('/api/1.0/group*', 'fixture:responses/group/group');

        // Открываем модалку
        cy.get('.amber-button', {timeout: 10000}).contains('Сотрудник').as('addButton');
        cy.get('@addButton').click();

        // Добавляем алиасы
        cy.get('.AddUsersForm').as('userForm');
        cy.get('@userForm').find('.amber-tabs__nav').as('tabs');
        cy.get('@userForm').contains('Сохранить').as('saveButton');
        cy.get('.AddUsersUserListV2User').as('userFields');
        cy.get('@userForm').find('.amber-button').contains('Сотрудник').as('addUserFieldsBtn');
        cy.get('[name="users.0.phone"]').as('phoneInput');
    });

    it('corptaxi-78: Проверка цифр в поле Телефон. Форма Добавление сотрудника', () => {
        cy.get('@phoneInput')
            .type('lol')
            .should('have.value', '+7')
            .type('12345{enter}')
            .end()
            .get('.amber-icon_warning')
            .should('exist')
            .end()
            .get('@phoneInput')
            .clear();
    });

    const USER = {
        fullname: 'Кирилл',
        phone: '+79559876612',
        email: 'kirill12@yandex.ru',
        ID: '001',
        taxiLimit: 1234,
        eatLimit: '1235'
    };

    function fillUserData() {
        cy.get('[name="users.0.fullname"]').type(USER.fullname);
        cy.get('[name="users.0.phone"]').clear().type(USER.phone);
        cy.get('[name="users.0.email"]').clear().type(USER.email);
        cy.get('[name="users.0.nickname"]').clear().type(USER.ID);
    }


    it('corptaxi-395: Добавление нового сотрудника. Вкладка Сотрудники', () => {
        cy.intercept('POST', '/api/1.0/client/*/user', {
            _id: '111'
        }).as('saveUser');
        fillUserData();

        cy.get('@saveButton').click();
        cy.wait('@saveUser').its('request.body')
            .then(body => {
                expect(body.fullname).eq(USER.fullname);
                expect(body.phone).eq(USER.phone);
                expect(body.email).eq(USER.email);
                expect(body.nickname).eq(USER.ID);
            });

    });

    it('corptaxi-398: Добавление сотрудника в группу. Вкладка Сотрудники', () => {
        cy.intercept('POST', '/api/1.0/client/*/user', {
            _id: '111'
        }).as('saveUser');

        fillUserData();

        cy.xpath('//*[text()="Группа"]/../..//input[@autocomplete="off"]').click();
        cy.get('.Select-menu-outer').contains('group').click();

        cy.get('@saveButton').click();
        cy.wait('@saveUser').its('request.body')
            .then(body => {
                expect(body.fullname).eq(USER.fullname);
                expect(body.phone).eq(USER.phone);
                expect(body.email).eq(USER.email);
                expect(body.nickname).eq(USER.ID);
                expect(body.role.role_id).eq(group.items[0]._id);
            });

    });



    it('corptaxi-157: Возможность заполнения добавленных полей в форме Добавление сотрудника', () => {
        cy.get('@addUserFieldsBtn').click().get('@userFields').should('have.length', 2);
        cy.get('[name="users.1.fullname"]').type(USER.fullname).should('have.value', USER.fullname);
        cy.get('[name="users.1.phone"]').clear().type(USER.phone).should('have.value', '+7 (955) 987 66 12');
        cy.get('[name="users.1.email"]').clear().type(USER.email).should('have.value', USER.email);
        cy.get('[name="users.1.nickname"]').clear().type(USER.ID).should('have.value', USER.ID);
        // Проверка удаляется ли первая форма
        cy.get('@userFields')
            .first()
            .find('.amber-icon_trash')
            .should('exist')
            .click()
            .end()
            .get('@userFields')
            .should('have.length', 1);
    });

    it('corptaxi-977: Ошибка при отправке пустой формы', () => {
        cy.get('@saveButton').click();
        cy.get('.amber-icon_warning').should('exist');
    });


    it('corptaxi-978: На вкладке "Сервисы" нет полей "Тариф" и "Лимит" для кастомной группы', () => {
        cy.get('.DepartmentAndRole__department').find('input').type('test1{enter}');
        cy.get('.DepartmentAndRole__role .Select-input').find('input').type('group{enter}');
        openServicesTab();

        //Такси
        cy.get('@ServicesConfSection').find('section').eq(0).contains('Лимит').should('not.exist');
        cy.get('@ServicesConfSection').find('section').eq(0).contains('Тариф').should('not.exist');

        //Еда
        cy.get('@ServicesConfSection').find('section').eq(1).contains('Лимит').should('not.exist');
        cy.get('@ServicesConfSection').find('section').eq(1).contains('Тариф').should('not.exist');

        // Драйв
        cy.get('@ServicesConfSection').find('section').eq(2).contains('Лимит').should('exist');
    });

    context('Открыта вкладка ограничений', () => {
        beforeEach(() => {
            openServicesTab();
        });

        it('corptaxi-176: Чекбокс «Включить» по умолчанию. Сервис Такси. Форма Добавление сотрудника', () => {
            const FAKE_NAME = 'Some Name';
            cy.get('[placeholder="Включить"]').eq(0).should('be.checked');
            cy.xpath('//*[@placeholder="Включить"]/..').eq(0).click();

            openEmployeeTab();
            cy.get('[name="users.0.fullname"]').type(FAKE_NAME);
            cy.get('@phoneInput').type('9045423816');
            cy.route({
                method: 'POST',
                url: '/api/1.0/client/*/user',
                response: {_id: '1234'}
            }).as('saveUser');
            cy.get('@saveButton').click();

            cy.wait('@saveUser')
                .its('request.body')
                .then(xhr => {
                    expect(xhr.phone).to.equal('+79045423816');
                    expect(xhr.department_id).to.be.null;
                    expect(xhr.fullname).to.equal(FAKE_NAME);
                    expect(xhr.email).to.be.empty;
                    expect(xhr.cost_centers_id).to.equal('134bab293df74fa1a86fe90e448bd527');
                    expect(xhr.is_active).to.be.false;
                    expect(xhr.role.classes).to.include.members([
                        'vip',
                        'premium_van',
                        'ultimate',
                        'maybach',
                        'cargo',
                        'child_tariff',
                        'express',
                        'business',
                        'comfortplus',
                        'courier',
                        'minivan',
                        'universal',
                        'econom'
                    ]);
                    expect(xhr.role.no_specific_limit).to.be.true;
                    expect(xhr.role.restrictions).to.be.empty;
                    expect(xhr.role.geo_restrictions).to.be.empty;
                    expect(xhr.role.period).to.equal('month');
                    expect(xhr.role.limits_mode).to.equal('and');
                    expect(xhr.role.orders.no_specific_limit).to.be.true;
                    expect(xhr.services.drive.is_active).to.be.false;
                    expect(xhr.services.drive.soft_limit).is.null;
                    expect(xhr.services.eats2.is_active).to.be.false;
                    expect(xhr.services.eats2.limits.monthly.amount).to.equal('-1');
                    expect(xhr.services.eats2.limits.monthly.no_specific_limit).to.be.true;
                });
        });
        context('Проверка лимита', () => {
            beforeEach(() => {
                //  cy.get('.Limit__checkbox').as('limitCheckboxTaxi');
                cy.get('.Limit__checkbox').as('limitCheckbox');
                cy.get('.Limit__input input').as('limitInput');
                cy.get('.UserFormEatsConfig').as('formEatsConfig');
                cy.get('.UserFormDriveConfig').as('formDriveConfig');
            });

            it('corptaxi-396: Добавление нового сотрудника с лимитами на сервисы. Вкладка Сотрудники', () => {
                cy.intercept('POST', '/api/1.0/client/*/user', {
                    _id: '111'
                }).as('saveUser');
                cy.get('@formEatsConfig')
                    .find('.amber-checkbox__content')
                    .eq(0)
                    .click()
                cy.get('@formEatsConfig')
                    .find('[type="text"]').eq(0)
                    .type(USER.eatLimit, {force: true})
                cy.get('@limitCheckbox').eq(0)
                    .click()
                    .get('@limitInput').eq(0)
                    .type(USER.taxiLimit)

                openEmployeeTab();
                fillUserData();
                cy.get('@saveButton').click();
                cy.wait('@saveUser').its('request.body')
                    .then(body => {
                        expect(body.fullname).eq(USER.fullname);
                        expect(body.phone).eq(USER.phone);
                        expect(body.email).eq(USER.email);
                        expect(body.nickname).eq(USER.ID);
                        expect(body.role.limit).eq(USER.taxiLimit);
                        expect(body.services.eats2.limits.monthly.amount).eq(USER.eatLimit);
                    });

            });

            it('corptaxi-188: Чекбокс «Без лимита» по умолчанию. Сервис Такси.', () => {
                cy.get('@limitCheckbox').find('input').should('be.checked');
                cy.get('@limitInput').should('be.disabled');
            });

            it('corptaxi-195: Проверка цифр в поле Лимит. Сервис Такси', () => {
                cy.get('@limitCheckbox')
                    .eq(0)
                    .click()
                    .get('@limitInput')
                    .eq(0)
                    .should('not.be.disabled')
                    .and('be.empty')
                    .get('@limitInput')
                    .eq(0)
                    .type('123')
                    .should('have.value', '123')
                    .get('@limitCheckbox')
                    .eq(0)
                    .find('input')
                    .should('not.be.checked')
                    .get('@limitCheckbox')
                    .eq(0)
                    .click()
                    .find('input')
                    .should('be.checked')
                    .get('@limitInput')
                    .eq(0)
                    .should('be.empty');
            });

            it('corptaxi-213: Возможность задать лимит при выключенном чекбоксе «Включить». Сервис Еда', () => {
                cy.get('@formEatsConfig')
                    .find('.amber-checkbox__content')
                    .eq(0)
                    .click()
                    .should('not.be.disabled');

                cy.get('@formEatsConfig')
                    .find('[type="text"]')
                    .type('123', {force: true})
                    .should('have.value', '123');
            });

            it('corptaxi-242: Проверка цифр в поле Лимит. Сервис Драйв', () => {
                cy.get('@formDriveConfig')
                    .find('.amber-checkbox__content')
                    .eq(0)
                    .click()
                    .should('not.be.disabled');

                cy.get('@formDriveConfig')
                    .find('[type="text"]')
                    .type('123')
                    .should('have.value', '123');
            });
        });

        context('Проверка лимита по времени', () => {
            beforeEach(() => {
                cy.get('.Restrictions__checkbox').as('restrictionsCheckbox').click();
            });

            it('corptaxi-491: Проверка работоспособности чек-боксов Дни недели. Раздел Сервисы', () => {
                cy.get('@restrictionsCheckbox').find('input').should('be.checked');
                cy.get('.RestrictionDay')
                    .should('have.length', 7)
                    .find('input')
                    .eq(0)
                    .should('not.be.checked')
                    .get('.RestrictionDay')
                    .eq(0)
                    .click()
                    .find('input')
                    .should('be.checked');
            });

            it('corptaxi-495: Проверка формата в первом поле Время. Раздел Сервисы', () => {
                cy.get('.RestrictionTime__start')
                    .find('input')
                    .should('have.value', '00:00')
                    .type('PSF}{.=')
                    .should('have.value', '00:00')
                    .clear()
                    .type('8000')
                    .blur()
                    .should('have.value', '80:00')
                    .and('have.attr', 'errors', 'Неверное значение часов')
                    .clear()
                    .type('2080')
                    .blur()
                    .should('have.value', '20:80')
                    .and('have.attr', 'errors', 'Неверное значение минут')
                    .clear()
                    .type('2020')
                    .should('have.value', '20:20')
                    .and('not.have.attr', 'errors');
            });

            it('corptaxi-510: Кнопка Добавить при выборе День недели/Время. Раздел Сервисы', () => {
                cy.get('.Restrictions__add')
                    .click()
                    .end()
                    .get('.Restriction')
                    .as('restriction')
                    .should('have.length', 2)
                    .end()
                    .get('.Restriction__remove')
                    .should('have.length', 2)
                    .eq(0)
                    .click()
                    .end()
                    .get('@restriction')
                    .should('have.length', 1);
            });
        });
    });
});
