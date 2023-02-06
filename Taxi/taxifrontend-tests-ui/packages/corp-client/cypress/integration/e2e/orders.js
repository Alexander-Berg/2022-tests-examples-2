import profileData from './data/orders.json';
import '../../support/ui-commands/orders';

describe('Отчёты', () => {
    const corpUser = 'autotestcorp-profile';
    const services = {taxi: 'Такси', drive: 'Драйв', eats: 'Еда'};

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.server();
        cy.route('post', '**/users', 'fixture:responses/orders/users.json').as('users');
        cy.route(
            'get',
            '/api/1.0/client/*/order?skip=0&limit=50&sorting_field=due_date&sorting_direction=-1',
            'fixture:responses/orders/response-taxi-orders.json'
        ).as('responseTaxiOrders');
        cy.route(
            'get',
            'api/1.0/client/*/user/*',
            'fixture:responses/orders/response-taxi-client.json'
        ).as('responseTaxiClient');
        cy.route(
            'get',
            'api/1.0/client/*/order/*',
            'fixture:responses/orders/response-taxi-order.json'
        ).as('responseTaxiOrder');
        cy.route(
            'get',
            'api/1.0/client/*/order/*/trackstory',
            'fixture:responses/orders/response-taxi-trackstory.json'
        ).as('responseTaxiTrackStory');
        cy.route(
            'get',
            'api/1.0/client/*/eats/orders?limit=50&offset=0',
            'fixture:responses/orders/response-eats-orders.json'
        ).as('responseEatsOrders');
        cy.route({
            method: 'put',
            url: '/api/1.0/client/*/order/*/change',
            response: [{}],
            status: '200'
        }).as('costStatusResponse');
        cy.route(
            'get',
            'api/1.0/client/*/drive/orders?offset=0&limit=50',
            'fixture:responses/orders/response-drive-orders.json'
        ).as('responseDriveOrders');
        cy.route('post', '/api/1.0/client/*/reports/orders/generate').as('generateExport');
        cy.route(
            'get',
            `/api/1.0/client/*/order?*&search=${profileData.taxi.button_cost_center}*`,
            'fixture:responses/orders/response-search-cost.json'
        ).as('searchCostCenter');
        cy.route(
            'api/1.0/client/*/order?skip=50&limit=50&sorting_field=due_date&sorting_direction=-1',
            'fixture:responses/orders/response-scrolling-orders.json'
        ).as('scrollingResponse');
        cy.corpOpen('orders/');
    });

    it('corptaxi-1020: Данные в списке отчётов (Яндекс.Такси)', () => {
        cy.orders.selectService(services.taxi);

        cy.get('.TableRow > .amber-col_paddingLeft-xs_m')
            .contains(profileData.taxi.name)
            .should('exist');
        cy.get('.TableRow > .amber-col_paddingRight-xs_s.amber-col_columns-xs_2')
            .contains(profileData.taxi.date_h)
            .should('exist');
        cy.get('.TableRow > .amber-col_paddingRight-xs_s.amber-col_columns-xs_2')
            .contains(profileData.taxi.date_d)
            .should('exist');
        cy.get('.TableRow > :nth-child(3) > .order-route-address')
            .contains(profileData.taxi.adress_1)
            .should('exist');
        cy.get('.TableRow > :nth-child(4) > .order-route-address')
            .contains(profileData.taxi.adress_3)
            .should('exist');
        cy.get('.TableRow > .amber-col_paddingRight-xs_m > .price')
            .contains(profileData.taxi.sum)
            .should('exist');
    });

    it('corptaxi-632: Проверка одной поездки', () => {
        cy.scrollTo('top');
        cy.get('.OrderGroup > .RowGroup > .TableRow > .amber-col_paddingLeft-xs_m', {
            timeout: 10000
        })
            .contains(profileData.taxi.name)
            .click();
        cy.wait('@responseTaxiOrder');
        cy.wait('@responseTaxiTrackStory');
        cy.get('.OrderDetails__id').contains(profileData.taxi.id).should('exist');
        cy.get('.OrderDetails__driver').contains(profileData.taxi.performer.car).should('exist');
        cy.get('.OrderDetails__driver')
            .contains(profileData.taxi.performer.fullname)
            .should('exist');
        cy.get('.OrderDetails__driver').contains(profileData.taxi.performer.phone).should('exist');
        cy.get('.RouteDescription__point_type_source > .amber-row > .amber-col')
            .contains(profileData.taxi.adress_1)
            .should('exist');
        cy.get('.RouteDescription__point_type_progress > .amber-row > .amber-col')
            .contains(profileData.taxi.adress_2)
            .should('exist');
        cy.get('.RouteDescription__point_type_destination > .amber-row > .amber-col')
            .contains(profileData.taxi.adress_3)
            .should('exist');
        cy.get('.OrderDetails__trip-details', {timeout: 10000}).contains('Связаться с поддержкой');
        cy.get('.OrderDetails__right ').contains(profileData.taxi.status).should('exist');
        cy.get('.OrderDetails__right ').contains(profileData.taxi.tariff).should('exist');
        cy.get('.OrderDetails__right ').contains(profileData.taxi.cost_center).should('exist');
        cy.get('.OrderDetails__right ').contains(profileData.taxi.order_method).should('exist');
        cy.get('.OrderDetails__right ').contains(profileData.taxi.sum).should('exist');
    });

    it('corptaxi-1021: Проверка кнопки (Перейти в профиль)', () => {
        cy.orders.selectService(services.taxi);

        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            profileData.taxi.button_cost_center
        );
        cy.wait('@searchCostCenter');
        cy.get('[title="Россия, Москва, Лесная улица, 41"]').nhover();
        cy.get('.amber-button__text').contains('Перейти в профиль').click();
        cy.url().should('contain', profileData.taxi.profile_link);
    });

    it('corptaxi-1022: Проверка кнопки (Повторить)', () => {
        cy.orders.selectService(services.taxi);

        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            profileData.taxi.button_cost_center
        );
        cy.wait('@searchCostCenter');
        cy.get('[title="Россия, Москва, Лесная улица, 41"]').nhover();
        cy.get('.amber-button__text').contains('Повторить').click();
        cy.url().should('contain', profileData.taxi.reload_link);
    });

    it('corptaxi-1023: Проверка кнопки (Где водитель?)', () => {
        cy.orders.selectService(services.taxi);

        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            profileData.taxi.button_cost_center
        );
        cy.wait('@searchCostCenter');
        cy.get('[title="Россия, Москва, Лесная улица, 41"]').nhover();
        cy.get('.amber-button__text').contains('Где водитель?').click();
        cy.url().should('contain', profileData.taxi.driver_link);
    });

    it('corptaxi-1024: Проверка кнопки (Отменить заказ)', () => {
        cy.orders.selectService(services.taxi);

        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            profileData.taxi.button_cost_center
        );
        cy.wait('@searchCostCenter');
        cy.get('[title="Россия, Москва, Лесная улица, 41"]').nhover();
        cy.get('.amber-button__text').contains('Отменить заказ').click();
        cy.url().should('contain', profileData.taxi.cancel_link);
    });

    it('corptaxi-1025: Проверка выпадашки (Текущие поездки)', () => {
        cy.scrollTo(500, 0);
        cy.get('.OrderGroup > .RowGroup__header > .amber-col > .amber-typography__headline')
            .contains('Текущие поездки')
            .click();
        cy.get('.RowGroup > .TableRow > .TableCell')
            .contains('Текущая поездка')
            .should('not.exist');
        cy.get('.OrderGroup > .RowGroup__header > .amber-col > .amber-typography__headline')
            .contains('Текущие поездки')
            .click();
        cy.get('.RowGroup > .TableRow > .TableCell').contains('Текущая поездка').should('exist');
    });

    it('corptaxi-1026: Проверка выпадашки (Будущие поездки)', () => {
        cy.get('.OrderGroup > .RowGroup__header > .amber-col > .amber-typography__headline')
            .contains('Будущие поездки')
            .click();
        cy.get('.RowGroup > .TableRow > .TableCell')
            .contains('Будущая поездка')
            .should('not.exist');
        cy.get('.OrderGroup > .RowGroup__header > .amber-col > .amber-typography__headline')
            .contains('Будущие поездки')
            .click();
        cy.get('.RowGroup > .TableRow > .TableCell').contains('Будущая поездка').should('exist');
    });

    it('corptaxi-1027: Проверка выпадашки (Прошлые поездки)', () => {
        cy.route(
            'get',
            'api/1.0/client/*/order?skip=0&limit=50&sorting_field=due_date&sorting_direction=-1',
            'fixture:responses/orders/response-taxi-orders-complete.json'
        ).as('responseTaxiOrders');
        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control');
        cy.get('.OrderGroup > .RowGroup__header > .amber-col > .amber-typography__headline')
            .contains('Прошлые поездки')
            .click();
        cy.get('.TableCell').should('not.exist');
        cy.get('.OrderGroup > .RowGroup__header > .amber-col > .amber-typography__headline')
            .contains('Прошлые поездки')
            .click();
        cy.get('.RowGroup > .TableRow > .TableCell').contains('Сергей Николаевич').should('exist');
    });

    it('corptaxi-1028: Проверка пагинации (Скролинг)', () => {
        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control');
        cy.scrollTo('top', 3000);
        cy.wait(400);
        cy.get('.RowGroup > .TableRow > .TableCell')
            .contains(profileData.taxi.scrolling)
            .should('exist');
    });

    it('corptaxi-1029: Поиск по центру затрат', () => {
        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            profileData.taxi.cost_center
        );
        cy.get('.OrderGroup > .RowGroup > .TableRow > .amber-col_paddingLeft-xs_m').should($res => {
            expect($res).to.have.length(1);
        });
    });

    it('corptaxi-1030: Поиск по центру затрат (Не существующий)', () => {
        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            'Не существующий'
        );

        cy.get('.TableRow > .BlankSlate__text').contains('Нет заказов').should('exist');
    });

    it('corptaxi-1031: Проверка списка Еды', () => {
        cy.orders.selectService(services.eats);

        cy.wait('@users');
        cy.wait('@responseEatsOrders');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.name).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.phone).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.date_h).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.date_d).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.whence).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.where).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.sum).should('exist');
    });

    it('corptaxi-1033: Проверка одного заказа Еды', () => {
        cy.orders.selectService(services.eats);

        cy.wait('@users');
        cy.wait('@responseEatsOrders');
        cy.get('.TableRow  > .TableCell').contains(profileData.eats.name).click();

        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.eats.status)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.eats.order.product_1.name)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.eats.order.product_1.amount)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.eats.order.delivery_sum)
            .should('exist');
    });

    it('corptaxi-1032: Проверка списка Драйва', () => {
        cy.orders.selectService(services.drive);

        cy.wait('@users');
        cy.wait('@responseDriveOrders');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.name).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.phone).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.date_h).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.date_d).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.whence).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.where).should('exist');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.sum).should('exist');
    });

    it('corptaxi-1034: Проверка одного заказа Драйва', () => {
        cy.orders.selectService(services.drive);

        cy.wait('@users');
        cy.wait('@responseDriveOrders');
        cy.get('.TableRow  > .TableCell').contains(profileData.drive.name).click();

        cy.get('.ymaps-2-1-79-map', {timeout: 10000}).should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.drive.duration)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.drive.km)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.drive.city)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.drive.avto)
            .should('exist');
        cy.get('.EatsOrderDetails > .amber-col_paddingBottom-xs_m')
            .contains(profileData.drive.tariff)
            .should('exist');
    });

    it('corptaxi-1035: Экспорт отчётов (Яндекс.Такси)(За текущий месяц)', () => {
        cy.orders.selectService(services.taxi);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('current');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1036: Экспорт отчётов (Яндекс.Такси)(За прошлый месяц)', () => {
        cy.orders.selectService(services.taxi);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('last');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1037: Экспорт отчётов (Яндекс.Такси)(За период)', () => {
        cy.orders.selectService(services.taxi);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('period', '01.08.2020', '23.09.2020');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1038: Экспорт отчётов (Яндекс.Еда)(За текущий месяц)', () => {
        cy.orders.selectService(services.eats);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('current');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1039: Экспорт отчётов (Яндекс.Еда)(За прошлый месяц)', () => {
        cy.orders.selectService(services.eats);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('last');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1040: Экспорт отчётов (Яндекс.Еда)(За период)', () => {
        cy.orders.selectService(services.eats);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('period', '01.08.2020', '23.09.2020');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1041: Экспорт отчётов (Яндекс.Драйв)(За текущий месяц)', () => {
        cy.orders.selectService(services.drive);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('current');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1042: Экспорт отчётов (Яндекс.Драйв)(За прошлый месяц)', () => {
        cy.orders.selectService(services.drive);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('last');
        cy.orders.closeExportModal();
    });

    it('corptaxi-1043: Экспорт отчётов (Яндекс.Драйв)(За период)', () => {
        cy.orders.selectService(services.drive);

        cy.wait('@responseTaxiOrders');
        cy.orders.generateExport('period', '01.08.2020', '23.09.2020');
        cy.orders.closeExportModal();
    });
});
