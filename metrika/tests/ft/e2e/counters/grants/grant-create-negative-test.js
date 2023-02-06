'use strict'

const {assert} = require('chai');
const {Passport} = require('../../../pageobjects/Passport.js');
const {EditCounterPage} = require('../../../pageobjects/EditCounterPage');
const {simpleUser: user} = require('../../../data/users');
const {goalCreateTestCounter: counter} = require('../../../data/counters');
const grantsData = require('../../../data/counterGransData');
const errors = require('../../../data/errorMessages');

beforeEach(function () {
    return new Passport(this.browser).login(user);
});

describe('Выдача доступа (негативные)', function () {
    let page;

    beforeEach(async function () {
        page = new EditCounterPage(this.browser);
        await page.openGrants(counter.id);
    })

    const wrongTestUsers = [
        {
            description: 'Несуществующий логин',
            user: grantsData.noneExistentUser,
            error: errors.USER_DOES_NOT_EXIST
        },
        {
            description: 'Логин владельца',
            user: user.username,
            error: errors.NOT_USE_OWNER_LOGIN
        },
        {
            description: 'Ранее добавленный логин',
            user: grantsData.existUser,
            error: errors.USER_ALREADY_EXIST
        },
        {
            description: 'Пустое поле',
            user: grantsData.emptyUser,
            error: errors.NOT_EMPTY
        },
        {
            description: 'Логин + @',
            user: grantsData.userWithInvalidLogin,
            error: errors.USER_DOES_NOT_EXIST
        },
        {
            description: 'Логин + почтовая система кроме яндекса',
            user: grantsData.userWithWrongMail,
            error: errors.USER_DOES_NOT_EXIST
        }
    ];

    wrongTestUsers.forEach(function (testUser) {
        it(`${testUser.description}`, async function () {
            await page.createGrant(testUser.user, false);
            const error = await page.getErrorMessage();
            assert.equal(error, testUser.error, 'ошибка совпадает');
        });

    });
});
