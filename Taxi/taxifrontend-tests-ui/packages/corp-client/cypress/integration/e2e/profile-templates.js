import profileData from './data/profile-templates.json';

describe('Шаблоны комментариев', () => {
    const corpUser = 'autotestcorp-profile';
    const templateRename = 'Rename' + Date.now();
    const templateDelete = 'Delete' + Date.now();
    let templateRenameId;

    before(() => {
        cy.removeAllTemplates(corpUser);
        cy.addTemplate(
            corpUser,
            templateRename,
            profileData.temp_comment_api,
            profileData.temp_tarif_api
        ).then(id => {
            templateRenameId = id;
        });
        cy.addTemplate(
            corpUser,
            templateDelete,
            profileData.temp_comment_api,
            profileData.temp_tarif_api
        );
    });

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.visit('profile/comment-templates/');
    });

    it('corptaxi-1051: Создание шаблона', () => {
        cy.visit('profile/comment-templates/');
        cy.get('.amber-col > .amber-button', {timeout: 10000})
            .contains('Добавить новый шаблон')
            .click();
        cy.get('[name="name"]').type(profileData.temp_name);
        cy.get('[name="comment"]').type(profileData.temp_comment);
        cy.get('.Select-input > input').click();
        cy.get('.Select-menu-outer').contains(profileData.temp_tarif).click();
        cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();

        cy.xpath(`//div[text()='${profileData.temp_name}']`, {timeout: 10000})
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get('[name="name"]').should('have.value', profileData.temp_name);
        cy.get('[name="comment"]').should('have.value', profileData.temp_comment);
        cy.get('.Select-value').contains(profileData.temp_tarif).should('exist');
        cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
        cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');
    });

    it('corptaxi-1052: Редактирование шаблона', () => {
        cy.xpath(`//div[text()='${templateRename}']`, {timeout: 10000})
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get('[name="name"]').clear().type(profileData.temp_name_api_rn);
        cy.get('[name="comment"]').clear().type(profileData.temp_comment_api_rn);
        cy.get('.Select-input > input').click();
        cy.get('.Select-menu-outer').contains(profileData.temp_tarif_api_rn).click();
        cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();

        cy.visit(`/profile/comment-templates#edit/${templateRenameId}`);
        cy.get('[name="name"]').should('have.value', profileData.temp_name_api_rn);
        cy.get('[name="comment"]').should('have.value', profileData.temp_comment_api_rn);
        cy.get('.Select-value').contains(profileData.temp_tarif_api_rn).should('exist');
        cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
        cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');
    });

    it('corptaxi-1053: Удаление шаблона', () => {
        cy.xpath(`//div[text()='${templateDelete}']`, {timeout: 10000})
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get('button.EditorModalFooterSection__remove').contains('Удалить').click();
        cy.get('button.amber-button_theme_accent').contains('Удалить').click();
        cy.xpath(
            `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${templateDelete}')]`
        ).should('not.exist');
    });
});
