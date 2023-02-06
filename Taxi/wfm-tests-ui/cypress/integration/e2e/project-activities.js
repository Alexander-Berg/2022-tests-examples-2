import profileData from './data/project-activities.json';

describe('Раздел Проектные активности', () => {
    const wfmUser = 'autotest-profile';

    before(() => {
        cy.globalRemProjActiv();
        cy.globalAddProjActiv();
    });

    beforeEach(() => {
        cy.yandexLogin(wfmUser);
    });

    after(() => {
        cy.globalRemProjActiv();
    });

    it('Просмотр Проектной активности', () => {
        cy.visit('/project-activities');
        cy.xpath(`//h4[text()='${profileData.name}']`).click();
        cy.get('[data-cy=project-activities-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=project-activities-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name
        );
        cy.get('[data-cy=project-activities-form-description]', {timeout: 10000}).should(
            'have.value',
            profileData.description
        );
    });

    it('Добавление Проектной активности', () => {
        cy.visit('/project-activities');
        cy.get('[data-cy=project-activities-list-add-new]').click();
        cy.get('[data-cy=project-activities-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=project-activities-form-name]').type(profileData.name_cr);
        cy.get('[data-cy=project-activities-form-description]').type(profileData.description);
        cy.get('[data-cy=project-activities-form-submit]').click();

        cy.visit('/project-activities');
        cy.xpath(`//h4[text()='${profileData.name_cr}']`).click();
        cy.get('[data-cy=project-activities-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=project-activities-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name_cr
        );
        cy.get('[data-cy=project-activities-form-description]', {timeout: 10000}).should(
            'have.value',
            profileData.description
        );
    });

    it('Редактирование Проектной активности', () => {
        cy.visit('/project-activities');
        cy.get('.ant-list-header', {timeout: 10000});
        cy.xpath(`//h4[text()="${profileData.name_rn}"]`).click();
        cy.get('[data-cy=project-activities-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=project-activities-form-name]')
            .clear()
            .type(profileData.name_rn + '_rn');
        cy.get('[data-cy=project-activities-form-description]')
            .clear()
            .type(profileData.description + 'description');
        cy.get('[data-cy=project-activities-form-submit]').click();

        cy.visit('/project-activities');
        cy.xpath(`//h4[text()="${profileData.name_rn + '_rn'}"]`).click();
        cy.get('[data-cy=project-activities-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=project-activities-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name_rn + '_rn'
        );
        cy.get('[data-cy=project-activities-form-description]', {timeout: 10000}).should(
            'have.value',
            profileData.description + 'description'
        );
    });

    it('Удаление Проектной активности', () => {
        cy.visit('/project-activities');
        cy.get('.ant-list-header', {timeout: 10000});
        cy.xpath(`//h4[text()="${profileData.name_del}"]`).click();
        cy.get('[data-cy=project-activities-card-info-tab]', {timeout: 10000})
            .contains('Информация')
            .should('exist');
        cy.get('[data-cy=project-activities-form-name]', {timeout: 10000}).should(
            'have.value',
            profileData.name_del
        );
        cy.get('[data-cy=project-activities-form-remove]').click();

        cy.visit('/project-activities');
        cy.get('.ant-list-header', {timeout: 10000});

        cy.xpath(`//h4[text()="${profileData.name_del}"]`).should('not.exist');
    });
});
