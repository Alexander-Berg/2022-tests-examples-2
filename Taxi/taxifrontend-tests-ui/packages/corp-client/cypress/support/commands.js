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

import 'cypress-file-upload';
import './form-commands';
import './mocks';
import './backend';

Cypress.Commands.add('setLoginCookies', cookies => {
    cy.visit('https://passport-test.yandex.ru/auth?new=0');
    cookies.forEach(cookie => {
        cy.setCookie(cookie.name, cookie.value);
    });
});

const tokensFile = 'cypress/fixtures/login-tokens.json';
const usersFile = 'cypress/fixtures/users.json';

Cypress.Commands.add('getUsersFile', () => {
    cy.task('readFileMaybe', usersFile).then(users => {
        if (Object.keys(users).length !== 0) return users;
        cy.request({
            method: 'GET',
            url: `https://vault-api.passport.yandex.net/1/versions/sec-01ew058w0t6d5ycykyj2k78773/`,
            headers: {
                Authorization: `OAuth ${Cypress.env('yavOauthToken')}`
            }
        })
            .then(response => {
                users = JSON.parse(response.body.version.value[0].value);
                cy.writeFile(usersFile, users);
            })
            .then(() => {
                return users;
            });
    });
});

Cypress.Commands.add('yandexLogin', (login, newPassport = false) => {
    cy.getUsersFile('users.json')
        .then(users => {
            const client = users[login];
            cy.task('readFileMaybe', tokensFile).then(tokens => {
                if (tokens[login]) {
                    cy.log('Залогинились с кешированными куками');
                    cy.setLoginCookies(tokens[login]);
                    return;
                }
                cy.log('Надо авторизоваться в паспорте');
                if (newPassport === true) {
                    cy.visit('https://passport-test.yandex.ru');
                    if (cy.url() === 'https://passport-test.yandex.ru/profile') {
                        return;
                    }
                    cy.server();
                    cy.route({
                        method: 'POST',
                        url: 'https://passport-test.yandex.ru/registration-validations/auth/multi_step/start'
                    }).as('authLogin');
                    cy.route({
                        method: 'POST',
                        url: 'https://passport-test.yandex.ru/registration-validations/auth/multi_step/commit_password'
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
                } else {
                    cy.visit('https://passport-test.yandex.ru/auth?new=0');
                    if (cy.url() === 'https://passport-test.yandex.ru/auth?new=0&uid=*') {
                        return;
                    }
                    cy.get('[id="login"]').type(client.login + '{enter}');
                    cy.get('[id="passwd"]').type(client.password + '{enter}');
                }
                cy.getCookie('Session_id').then(sessioniD => {
                    cy.getCookie('yandexuid').then(yandexuid => {
                        cy.getCookie('sessguard').then(sessguard => {
                            const cookies = [sessioniD, yandexuid, sessguard];
                            cy.writeFile(tokensFile, {
                                ...tokens,
                                [login]: cookies
                            });
                        });
                    });
                });
            });
        })
        .then(() => {
            cy.getCookie('Session_id').should('exist');
        });
});

Cypress.Commands.add('corpOpen', url => {
    cy.intercept('/api/1.0/client/*/contracts*').as('contracts');
    cy.visit(url);
    cy.wait('@contracts').then(interception => {
        if (interception.response.statusCode === 403) {
            cy.log('statusCode 403, reloading...');
            // логирует в билд-лог
            cy.task('log', 'statusCode 403, reloading...');
            cy.reload();
        }
    });
});

Cypress.Commands.add('corpAddSharedRoutes', () => {
    cy.server();
});

Cypress.Commands.add('overrideConfig', {prevSubject: false}, override => {
    cy.window().then(window => {
        window.overrideConfig(override);
    });
});

Cypress.Commands.add('resetConfig', {prevSubject: false}, () => {
    cy.window().then(window => {
        window.resetConfig();
    });
});

Cypress.Commands.add('clearAddress', {prevSubject: true}, subject => {
    cy.wrap(subject).find('.PointSelect__clear').click();
    cy.wait(400);
});

Cypress.Commands.add('chooseAddressOption', {prevSubject: true}, (subject, text) => {
    cy.wrap(subject).find('.SuggestOption_selected', {timeout: 10000}).contains(text).click();
});

Cypress.Commands.add('fillAddress', {prevSubject: true}, (subject, params, suggestText) => {
    cy.wrap(subject).find('input').focus().type(params);
    cy.wrap(subject).chooseAddressOption(suggestText || params);
});

// TODO: заставить это работать
const methods = {
    address: {
        fill: (subject, value) => {
            cy.get(subject).fillAddress(value);
        },
        clear: () => undefined
    }
};

Cypress.Commands.add('assertFieldError', {prevSubject: true}, subject => {
    cy.wrap(subject).find('.ErrorWrapper').should('have.class', 'ErrorWrapper_error');
});

Cypress.Commands.add('getModal', {prevSubject: false}, className =>
    cy.get(`.amber-modal${className || ''}`)
);

Cypress.Commands.add('prepareLocalStorage', () => {
    window.localStorage.setItem(
        'onboarding',
        '{"staff.navigation":{"step":1},"versions.switch.latest":{"step":1},' +
            '"versions.switch.stable":{"step":1},"whatsnew":{"step":1}}'
    );
    cy.request({url: '/api/auth', headers: {'X-Application-Version': '0.0.82'}}).then(response => {
        const clientId = response.body.client_id;
        window.localStorage.setItem(`${clientId}.corp-client.push.timestamp`, Date.now());
        window.localStorage.setItem(`${clientId}.corp-client.header.v2.showOnboarding`, 'false');
    });
});
