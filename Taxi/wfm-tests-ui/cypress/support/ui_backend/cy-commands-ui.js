import profileAbsences from '../../integration/e2e/data/absences.json';
import profileProjActiv from '../../integration/e2e/data/project-activities.json';

var wfmUser = 'autotest-profile';

Cypress.Commands.add('getPlannig', (skill, date_from, date_to) => {
    cy.get('[data-cy=shifts-planning-filter-skills]', {timeout: 100000}).type(skill);
    cy.get('.ant-select-item-option-content', {timeout: 10000}).contains(skill).click();
    cy.get('[placeholder="С"]').click().type(date_from);
    cy.get('[placeholder="По"]')
        .click()
        .type(date_to + `{enter}`);
    cy.get('[data-cy=shifts-planning-filter-submit]').click();
});

Cypress.Commands.add('savePlanFifteen', (pl_0, pl_01, pl_02, pl_03) => {
    cy.get(':nth-child(36) > :nth-child(2) > .plan-cell').click().clear().type(pl_0);
    cy.get(':nth-child(39) > :nth-child(2) > .plan-cell').click().clear().type(pl_01);
    cy.get(':nth-child(43) > :nth-child(2) > .plan-cell').click().clear().type(pl_02);
    cy.get(':nth-child(51) > :nth-child(2) > .plan-cell').click().clear().type(pl_03);
    cy.get('[data-cy=shifts-planning-plan-fact-table-footer-save-plan]').click();
});

Cypress.Commands.add('savePlan', i => {
    for (let num = 1; num <= i; num++) {
        cy.get(':nth-child(' + num + ') > :nth-child(2) > .plan-cell')
            .click()
            .clear()
            .type(num);
    }
    cy.get('[data-cy=shifts-planning-plan-fact-table-footer-save-plan]').click();
});

Cypress.Commands.add('checkPlan', (i, diff) => {
    for (let num = 1; num <= i; num++) {
        cy.get(':nth-child(' + num + ') > :nth-child(2) > .plan-cell').contains(num);
        if (diff === true) {
            cy.get(':nth-child(' + num + ') > .critical-diff-cell').contains('-' + num);
        }
    }
});

Cypress.Commands.add('globalRemAbsences', () => {
    cy.yandexLogin(wfmUser);
    cy.removeAbsencesType(wfmUser, profileAbsences.name);
    cy.removeAbsencesType(wfmUser, profileAbsences.name_cr);
    cy.removeAbsencesType(wfmUser, profileAbsences.name_del);
    cy.removeAbsencesType(wfmUser, profileAbsences.name_rn);
    cy.removeAbsencesType(wfmUser, profileAbsences.name_rn + '_rn');
});

Cypress.Commands.add('globalAddAbsences', () => {
    cy.yandexLogin(wfmUser);
    cy.addAbsencesType(wfmUser, profileAbsences.name, profileAbsences.description);
    cy.addAbsencesType(wfmUser, profileAbsences.name_del, profileAbsences.description);
    cy.addAbsencesType(wfmUser, profileAbsences.name_rn, profileAbsences.description);
});

Cypress.Commands.add('globalRemProjActiv', () => {
    cy.yandexLogin(wfmUser);
    cy.removeProjectActivities(wfmUser, profileProjActiv.name);
    cy.removeProjectActivities(wfmUser, profileProjActiv.name_cr);
    cy.removeProjectActivities(wfmUser, profileProjActiv.name_del);
    cy.removeProjectActivities(wfmUser, profileProjActiv.name_rn);
    cy.removeProjectActivities(wfmUser, profileProjActiv.name_rn + '_rn');
});

Cypress.Commands.add('globalAddProjActiv', () => {
    cy.yandexLogin(wfmUser);
    cy.addProjectActivities(wfmUser, profileProjActiv.name, profileProjActiv.description);
    cy.addProjectActivities(wfmUser, profileProjActiv.name_del, profileProjActiv.description);
    cy.addProjectActivities(wfmUser, profileProjActiv.name_rn, profileProjActiv.description);
});
