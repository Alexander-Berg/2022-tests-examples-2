Cypress.Commands.add('mockDefaults', () => {
    cy.server();
    // Делаем так, чтобы всё не замоканное громко валилось и не давало забыть о себе
    cy.route({
        method: 'GET',
        url: '*',
        status: 500,
        response: {}
    }).as('failingGET');
    cy.route({
        method: 'POST',
        url: '*',
        status: 500,
        response: {}
    }).as('failingPOST');
    cy.route({
        method: 'PUT',
        url: '*',
        status: 500,
        response: {}
    }).as('failingPUT');
    cy.route('/api/auth', 'fixture:responses/auth/index').as('auth');
    cy.route('/api/1.0/client/*/announcements', 'fixture:responses/announcements/index').as(
        'announcements'
    );
    cy.route('/api/1.0/client/*', 'fixture:responses/client/index').as('currentClient');
    cy.route('/api/1.0/class*', 'fixture:responses/class/200').as('tariffs');
    cy.route(
        'POST',
        '/api/1.0/search/departments',
        'fixture:responses/search/departments/index'
    ).as('defaultAllDepartments');
    cy.route('/api/1.0/client/*/role/8fffcb*', 'fixture:responses/role/no-order-permission').as(
        'noOrderPermissionRole'
    );
    cy.route('/api/1.0/client/*/department?limit=1000', 'fixture:responses/department/index').as(
        'topLevelDepartments'
    );
    cy.route(
        '/api/1.0/client/*/department/544',
        'fixture:responses/department/bookkeeping-children'
    ).as('children');
    cy.route(
        '/api/1.0/client/*/role/?department_id=null&limit=*',
        'fixture:responses/role/top-level'
    ).as('topLevelRoles');
    cy.route(
        '/api/1.0/client/*/user/11ae63dbbbdb429b84a94482749189ad',
        'fixture:responses/user/normal'
    ).as('user');
    cy.route('POST', '/client-api/3.0/nearestzone', 'fixture:responses/nearestzone/index').as(
        'nearestzone'
    );
    cy.route('/api/1.0/client/*/order?*', 'fixture:responses/order/previous').as('clientOrders');
    cy.route('POST', '/client-api/3.0/zoneinfo', 'fixture:responses/zoneinfo/index').as('zoneinfo');
    cy.route('POST', '/client-api/3.0/geosearch', 'fixture:responses/geosearch/index').as(
        'geosearch'
    );
    cy.route(
        'GET',
        '/api/1.0/client/*/order/00bb4c150dbd29efaa3ccce0f321a394/progress',
        'fixture:responses/order/progress/200-expired'
    ).as('expiredOrderProgress');
    cy.route('/api/1.0/client/*/role/?department_id=524*', 'fixture:responses/role/for-booking').as(
        'bookingDepartmentRoles'
    );
    // Группа "без права самостоятельного заказа"
    cy.route('/api/1.0/client/*/role/8fffcb9488a54c9b9ad1a70bdd91972c', {
        _id: '8fffcb9488a54c9b9ad1a70bdd91972c',
        name: 'Без права самостоятельного заказа',
        counters: {users: 114},
        limit: 0,
        no_specific_limit: false,
        deletable: false,
        putable: false,
        is_cabinet_only: true,
        classes: ['vip', 'econom', 'express', 'comfortplus', 'cargo', 'business']
    });

    cy.route(
        'POST',
        '/api/1.0/client/*/department_manager/search',
        'fixture:responses/department_manager/search/index'
    ).as('defaultDepartmentManagers');
});
