import fieldsHandlers from './utils/field-handlers';

// Form fields assertations
Cypress.Commands.add(
    'assertFieldInvalid',
    {
        prevSubject: true
    },
    $subject => {
        cy.wrap($subject).find('.ErrorWrapper').should('have.class', 'ErrorWrapper_error');
    }
);

Cypress.Commands.add(
    'assertFieldValid',
    {
        prevSubject: true
    },
    $subject => {
        cy.wrap($subject).find('.ErrorWrapper').should('not.have.class', 'ErrorWrapper_error');
    }
);

Cypress.Commands.add(
    'assertFieldError',
    {
        prevSubject: true
    },
    ($subject, messageText) => {
        // eslint-disable-next-line cypress/no-assigning-return-values
        let el = cy.wrap($subject).next();

        el.should('have.class', 'ErrorWrapper__errors');
        if (messageText) {
            el.should('have.text', messageText);
        }
    }
);

// Form controls commands
Cypress.Commands.add(
    'fillTextInput',
    {
        prevSubject: true
    },
    ($subject, text) => {
        cy.wrap($subject).find('input').type(text);

        return cy.wrap($subject);
    }
);

Cypress.Commands.add(
    'clearTextInput',
    {
        prevSubject: true
    },
    $subject => {
        cy.wrap($subject).find('input').clear();

        return cy.wrap($subject);
    }
);

Cypress.Commands.add(
    'fillSelect',
    {
        prevSubject: true
    },
    ($subject, optionText) => {
        cy.wrap($subject).click().find('.Select-menu-outer').contains(optionText).click();

        return cy.wrap($subject);
    }
);

Cypress.Commands.add(
    'clearSelect',
    {
        prevSubject: true
    },
    $subject => {
        const $clearButton = $subject.find('.Select-clear');

        if ($clearButton.length) {
            cy.wrap($clearButton).click();
        }
        cy.wrap($subject).find('input').clear();

        return cy.wrap($subject);
    }
);

const getUnknownHandlerError = (fieldType, handlerType) =>
    `Нет соответствующего хендлера ${handlerType} для поля типа ${fieldType}`;

Cypress.Commands.add(
    'clearFieldControl',
    {
        prevSubject: true
    },
    ($subject, type) => {
        const HANDLER_TYPE = 'clear';
        const method = fieldsHandlers.getFieldHandler(type, HANDLER_TYPE);

        if (!method) {
            throw new Error(getUnknownHandlerError(type, HANDLER_TYPE));
        }

        return cy.wrap($subject)[method]();
    }
);

Cypress.Commands.add(
    'clearFormFields',
    {
        prevSubject: false
    },
    fieldsArr => {
        fieldsArr.forEach(({selector, type = 'input'}) => {
            cy.get(selector).clearFieldControl(type);
        });
    }
);
