const selectCostCenter = type => {
    cy.xpath('//*[@name="cost_centers.format"]/..').type(type + '{enter}');
    cy.xpath('//*[@name="cost_centers.required"]/..').click();
};

describe('Проверка старых кост-центров при добавлении сотрудников', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();
        cy.corpOpen('/staff');
        cy.server();
        cy.route('GET', '/api/1.0/client/*/cost_centers', 'fixture:responses/search/user/empty').as(
            'emptyCost'
        );
        // Открываем модалку
        cy.get('.amber-button', {timeout: 10000}).contains('Сотрудник').click();
        // Добавляем алиасы
        cy.get('.AddUsersForm').as('userForm');
        cy.get('@userForm').contains('Сохранить').as('saveButton');
        cy.get('@userForm').contains('Сервисы').click();
    });

    it('corptaxi-1060: Вкладка ограничений - по умолчанию выбирает "Свободно" для кост-центра', () => {
        cy.wait('@emptyCost');
        cy.get('.amber-select').contains('Свободный ввод').should('exist');
    });

    it('corptaxi-1061: Обязательность цз для "из списка" и "цз обязятелен"', () => {
        selectCostCenter('Из списка');
        cy.get('@saveButton').click();

        cy.get('.ErrorWrapper__errors')
            .contains('Добавьте хотя бы одно значение в список')
            .should('exist');
    });

    it('corptaxi-1062: Создание клиента с цетром затрат (старые цз)', () => {
        selectCostCenter('Из списка');
        cy.xpath('//*[@name="cost_centers.values"]/..').type('costCenter1{enter}costCenter2');
        cy.get('@userForm').contains('Сотрудники').click();
        cy.get('[name="users.0.fullname"]').type('Name');
        cy.get('[name="users.0.phone"]').type('9045423816');
        cy.route({
            method: 'POST',
            url: '/api/1.0/client/*/user',
            response: {_id: '1234'}
        }).as('saveUser');
        cy.get('@saveButton').click();

        cy.wait('@saveUser')
            .its('request.body')
            .then(xhr => {
                expect(xhr.cost_centers).to.eql({
                    required: true,
                    format: 'select',
                    values: ['costCenter1', 'costCenter2']
                });
                expect(xhr.cost_center).to.be.empty;
            });
    });
});
