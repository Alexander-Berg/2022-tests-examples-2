import profileData from './data/absences.json';

describe('Раздел Отсутствий', () => {
    const wfmUser = 'autotest-profile';

    before(() => {
        cy.globalRemAbsences();
        cy.globalAddAbsences();
    });

    beforeEach(() => {
        cy.yandexLogin(wfmUser);
    });

    after(() => {
        cy.globalRemAbsences();
    });

    it('Просмотр отсутствия', () => {
        cy.visit('/absences');
        cy.xpath(`//h4[text()='${profileData.name}']`).click();
        cy.get('[data-cy=absences-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=absences-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name
        );
        cy.get('[data-cy=absences-form-description]', {timeout: 10000}).should(
            'have.value',
            profileData.description
        );
    });

    it('Добавление отсутствия', () => {
        cy.visit('/absences');
        cy.get('[data-cy=absences-list-add-new]').click();
        cy.get('[data-cy=absences-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=absences-form-name]').type(profileData.name_cr);
        cy.get('[data-cy=absences-form-description]').type(profileData.description);
        cy.get('[data-cy=absences-form-submit]').click();

        cy.visit('/absences');
        cy.xpath(`//h4[text()='${profileData.name_cr}']`).click();
        cy.get('[data-cy=absences-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=absences-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name_cr
        );
        cy.get('[data-cy=absences-form-description]', {timeout: 10000}).should(
            'have.value',
            profileData.description
        );
    });

    it('Редактирование отсутствия', () => {
        cy.visit('/absences');
        cy.get('.ant-list-header', {timeout: 10000});
        cy.xpath(`//h4[text()="${profileData.name_rn}"]`).click();
        cy.get('[data-cy=absences-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=absences-form-name]')
            .clear()
            .type(profileData.name_rn + '_rn');
        cy.get('[data-cy=absences-form-description]')
            .clear()
            .type(profileData.description + 'description');
        cy.get('[data-cy=absences-form-submit]').click();

        cy.visit('/absences');
        cy.xpath(`//h4[text()="${profileData.name_rn + '_rn'}"]`).click();
        cy.get('[data-cy=absences-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=absences-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name_rn + '_rn'
        );
        cy.get('[data-cy=absences-form-description]', {timeout: 10000}).should(
            'have.value',
            profileData.description + 'description'
        );
    });

    it('Удаление отсутствия', () => {
        cy.visit('/absences');
        cy.get('.ant-list-header', {timeout: 10000});
        cy.xpath(`//h4[text()="${profileData.name_del}"]`).click();
        cy.get('[data-cy=absences-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=absences-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name_del
        );
        cy.get('[data-cy=absences-form-remove]').click();
        cy.get('.ant-popover-buttons > .ant-btn-primary').click();

        cy.visit('/absences');
        cy.get('.ant-list-header', {timeout: 10000});

        cy.xpath(`//h4[text()="${profileData.name_del}"]`).should('not.exist');
    });
});
