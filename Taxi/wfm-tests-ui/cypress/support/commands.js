// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

import './backend';
import './ui_backend/cy-commands-ui';

Cypress.Commands.add('setLoginCookies', cookies => {
    cookies.forEach(cookie => {
        cy.setCookie(cookie.name, cookie.value);
    });
});

const tokensFile = 'cypress/fixtures/login-tokens.json';
const usersFile = 'cypress/fixtures/users.json';

Cypress.Commands.add('getUsersFile', () => {
    cy.task('readFileMaybe', usersFile).then(users => {
        if (Object.keys(users).length !== 0) return users;
    });
});

Cypress.Commands.add('yandexLogin', login => {
    cy.getUsersFile('users.json').then(users => {
        const client = users[login];
        cy.task('readFileMaybe', tokensFile).then(tokens => {
            if (tokens[login]) {
                cy.log('Залогинились с кешированными куками');
                cy.setLoginCookies(tokens[login]);
                return;
            }
            cy.log('Надо авторизоваться в паспорте');
            cy.visit('https://passport-test.yandex.ru');
            if (cy.url() === 'https://passport-test.yandex.ru/profile') {
                return;
            }
            cy.server();
            cy.route({
                method: 'POST',
                url:
                    'https://passport-test.yandex.ru/registration-validations/auth/multi_step/start'
            }).as('authLogin');
            cy.route({
                method: 'POST',
                url:
                    'https://passport-test.yandex.ru/registration-validations/auth/multi_step/commit_password'
            }).as('authPassword');
            cy.route({
                method: 'POST',
                url: 'https://passport-test.yandex.ru/registration-validations/billing.cardsinfo'
            }).as('authPost1');
            cy.route({
                method: 'POST',
                url: 'https://passport-test.yandex.ru/registration-validations/get.addresses'
            }).as('authPost2');

            cy.route({
                method: 'POST',
                url: 'https://passport-test.yandex.ru/bla'
            }).as('phone');

            cy.server();
            cy.get('#passp-field-login')
                .focus()
                .wait(100)
                .type(client.login + '{enter}')
                .should('have.value', client.login);
            cy.wait('@authLogin');
            cy.get('#passp-field-passwd')
                .focus()
                .wait(100)
                .type(client.password + '{enter}')
                .should('have.value', client.password);
            cy.wait('@authPassword');

            cy.getCookies().then(cookie => {
                cy.writeFile(tokensFile, {
                    ...tokens,
                    [login]: cookie
                });
            });
        });
    });
});
