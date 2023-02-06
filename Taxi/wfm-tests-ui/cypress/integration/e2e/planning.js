import profileData from './data/planning.json';

describe('Раздел Планирование смен', () => {
    const wfmUser = 'autotest-profile';

    before(() => {});
    beforeEach(() => {
        cy.yandexLogin(wfmUser);
        cy.visit('/shifts/planning');
    });

    it('Загрузка страницы и проверка интерфейса', () => {
        cy.get('[data-cy=shifts-planning-filter-skills]', {timeout: 10000}).should('exist');
        cy.get('[data-cy=shifts-planning-filter-date-picker]').should('exist');
        cy.get('[data-cy=shifts-planning-filter-submit]').should('exist');
        cy.get('[data-cy=component-header-settings-btn]').should('exist');
    });

    it('Проверка таблицы по умолчанию (60 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);

        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.get(
            '[data-cy=shifts-planning-plan-fact-table] > thead > :nth-child(1) > :nth-child(2)'
        ).contains(`${profileData.pl_date_name}`);
        cy.get('[data-cy="shifts-planning-plan-fact-table"]')
            .find('.fixed-column')
            .should('have.length', 25);
    });

    it('Проверка таблицы по умолчанию (15 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);

        cy.get('[data-cy=component-header-settings-btn]').click();
        cy.get('[data-cy=shifts-planning-settings-granularity]').click();
        cy.get('[label="15 мин."]').click();
        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.get('[data-cy="shifts-planning-plan-fact-table"]')
            .find('.fixed-column')
            .should('have.length', 97);
    });

    it('Проверка ручного сохранения планирования (60 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);

        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.savePlan(7);

        cy.get('.ant-notification-notice', {timeout: 10000}).should('exist');
        cy.checkPlan(7, true);
    });

    it('Проверка ручного сохранения планирования (15 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);
        cy.get('[data-cy=component-header-settings-btn]').click();
        cy.get('[data-cy=shifts-planning-settings-granularity]').click();
        cy.get('[label="15 мин."]').click();

        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.savePlan(10);

        cy.get('.ant-notification-notice', {timeout: 10000}).should('exist');
        cy.checkPlan(10, true);
    });

    it('Преобразование сохраненного плана из 60 мин в 15 мин', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);

        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.savePlan(5);

        cy.get('.ant-notification-notice', {timeout: 10000}).should('exist');

        cy.get('[data-cy=component-header-settings-btn]').click();
        cy.get('[data-cy=shifts-planning-settings-granularity]').click();
        cy.get('[label="15 мин."]').click();

        cy.get(':nth-child(1) > :nth-child(2) > .plan-cell').contains(`1`);
        cy.get(':nth-child(2) > :nth-child(2) > .plan-cell').contains(`1`);
        cy.get(':nth-child(3) > :nth-child(2) > .plan-cell').contains(`1`);
        cy.get(':nth-child(4) > :nth-child(2) > .plan-cell').contains(`1`);
    });

    it('Проверка  часов FTE (15 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);
        cy.get('[data-cy=component-header-settings-btn]').click();
        cy.get('[data-cy=shifts-planning-settings-granularity]').click();
        cy.get('[label="15 мин."]').click();

        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.savePlanFifteen(
            profileData.pl_0,
            profileData.pl_01,
            profileData.pl_02,
            profileData.pl_03
        );

        cy.get('.hours', {timeout: 10000}).should('exist');

        cy.get('.ant-notification-close-x > .anticon > svg > path').click();
        cy.get('[data-cy=component-filter-pfd-measure-mode-picker-select]').click();
        cy.get('.ant-select-item-option-content').contains('Часы (FTE)').click();

        cy.get(':nth-child(36) > :nth-child(2) > .plan-cell').contains(`${profileData.fte_0}`);
        cy.get(':nth-child(39) > :nth-child(2) > .plan-cell').contains(`${profileData.fte_01}`);
        cy.get(':nth-child(43) > :nth-child(2) > .plan-cell').contains(`${profileData.fte_02}`);
        cy.get(':nth-child(51) > :nth-child(2) > .plan-cell').contains(`${profileData.fte_03}`);
        cy.get(':nth-child(36) > .critical-diff-cell').contains(`-${profileData.fte_0}`);
        cy.get(':nth-child(39) > .critical-diff-cell').contains(`-${profileData.fte_01}`);
        cy.get(':nth-child(43) > .critical-diff-cell').contains(`-${profileData.fte_02}`);
        cy.get(':nth-child(51) > .critical-diff-cell').contains(`-${profileData.fte_03}`);
    });

    it('Проверка Импорта  (60 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);

        cy.get('.hours', {timeout: 10000}).should('exist');

        const fileName = 'xlsxdata/file_hours.xlsx';
        cy.fixture(fileName, 'binary')
            .then(Cypress.Blob.binaryStringToBlob)
            .then(fileContent => {
                cy.get('[type="button"]').contains('Импорт').click();
                cy.get('[type="file"]').attachFile({
                    fileContent,
                    fileName,
                    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    encoding: 'utf8'
                });
            });

        cy.get(':nth-child(10) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_0}`);
        cy.get(':nth-child(13) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_01}`);
        cy.get(':nth-child(18) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_02}`);
        cy.get(':nth-child(24) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_03}`);
    });

    it('Проверка Импорта  (15 мин)', () => {
        cy.getPlannig(profileData.planning_name, profileData.pl_date_from, profileData.pl_date_to);
        cy.get('.hours', {timeout: 10000}).should('exist');
        cy.get('[data-cy=component-header-settings-btn]').click();
        cy.get('[data-cy=shifts-planning-settings-granularity]').click();
        cy.get('[label="15 мин."]').click();
        cy.get('.hours', {timeout: 10000}).should('exist');

        const fileName = 'xlsxdata/file-15m.xlsx';
        cy.fixture(fileName, 'binary')
            .then(Cypress.Blob.binaryStringToBlob)
            .then(fileContent => {
                cy.get('[type="button"]').contains('Импорт').click();
                cy.get('[type="file"]').attachFile({
                    fileContent,
                    fileName,
                    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    encoding: 'utf8'
                });
            });

        cy.get(':nth-child(2) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_0}`);
        cy.get(':nth-child(8) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_01}`);
        cy.get(':nth-child(14) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_02}`);
        cy.get(':nth-child(20) > :nth-child(2) > .plan-cell').contains(`${profileData.pl_03}`);
    });
});
