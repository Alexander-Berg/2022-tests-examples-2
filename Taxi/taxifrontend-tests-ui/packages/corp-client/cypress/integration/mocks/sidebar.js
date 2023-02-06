context('Сайдбар', () => {
    beforeEach(() => {
        // Логинимся, переходим на главную
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();
        cy.intercept('/api/1.0/search/departments', {fixture: 'responses/search/departments'});
    });

    context('Нормальная загрузка с сервера', () => {
        beforeEach(() => {
            // Добавляем алиасы
            cy.visit('/staff');
            cy.get('.MuiBox-root.MuiGrid-container').first().as('department_menu').should('exist');
            cy.get('@department_menu').find('input').as('search');
            cy.get('.Scrollable__inner-scrollable').as('mainList');
            cy.get('@mainList').children().as('listItems');
        });

        it('corptaxi-967: Проверка открытия/закрытия подразделений', () => {
            // Подпункты должны появляться только после клика на элемент списка
            cy.xpath('//div[text()="test"]').should('not.exist');
            cy.xpath('//div[text()="group1"]').should('not.exist');
            cy.intercept('/api/1.0/group?department_id=5b6177aca60946709d6d55d8357c7b7f', {
                fixture: 'responses/group/group_sidebar'
            });
            cy.xpath('//div[text()="test1.1"]').click();
            cy.xpath('//div[text()="test"]').should('be.visible');
            cy.xpath('//div[text()="group1"]').should('not.exist');
            cy.xpath('//div[text()="test"]').click();
            cy.xpath('//div[text()="group1"]').should('be.visible');
            // При клике на другой элемент списка подпункты должны пропадать
            cy.xpath('//div[text()="test1"]').click();
            cy.xpath('//div[text()="test"]').should('not.exist');
            cy.xpath('//div[text()="group1"]').should('not.exist');
        });
        it('corptaxi-968: Проверка ошибки в садбаре при загрузке групп', () => {
            cy.intercept('/api/1.0/group*', {
                statusCode: 400
            }).as('sidebarGroups');
            cy.xpath('//div[text()="test1.1"]').click();
            cy.wait('@sidebarGroups');
            //проверка на алерт в сайдбаре
            cy.get('.MuiBox-root.MuiGrid-container:first-child')
                .find('.amber-alert')
                .contains('componentStack')
                .should('exist');
            //проверка на 400 ошибку в правом нижнем углу
            cy.get('.Notification__message-item').contains('400').should('exist');
        });

        it('corptaxi-969: Проверка наличия кнопок редактирования', () => {
            cy.intercept('/api/1.0/group?department_id=5b6177aca60946709d6d55d8357c7b7f', {
                fixture: 'responses/group/group_sidebar'
            });
            cy.get('[href="/staff/departments/d95049ed915b4769bf4501599cc555e7"]').click();
            cy.get(
                '[href="/staff/departments/d95049ed915b4769bf4501599cc555e7/5b6177aca60946709d6d55d8357c7b7f"]'
            ).nhover();
            // Есть кнопка редактирования у дочернего подразделения
            cy.get(
                `[href="/staff/departments/d95049ed915b4769bf4501599cc555e7/5b6177aca60946709d6d55d8357c7b7f"] > div > div > button:last-child`
            ).click();
            cy.get('.DepartmentForm').should('exist');
            cy.get('.ModalCloseButton').click();
            cy.xpath('//div[text()="test"]').click();
            // Есть кнопка редактирования у группы
            cy.get('[href="/staff/departments/d95049ed915b4769bf4501599cc555e7"]').click();
            cy.get(
                '[href="/staff/departments/d95049ed915b4769bf4501599cc555e7/5b6177aca60946709d6d55d8357c7b7f"]'
            ).click();
            cy.get(
                `[href="/staff/departments/d95049ed915b4769bf4501599cc555e7/5b6177aca60946709d6d55d8357c7b7f/groups/e86031fe399e4be297207fc5f02eb709"]`
            ).nhover();
            cy.get(
                `[href="/staff/departments/d95049ed915b4769bf4501599cc555e7/5b6177aca60946709d6d55d8357c7b7f/groups/e86031fe399e4be297207fc5f02eb709"] > div > div > button:last-child`
            ).click();
            cy.get('.amber-modal__window-inner').should('exist');
            cy.get('.ModalCloseButton').click();
        });
    });
});
