'use strict'

const {assert} = require('chai');
const {Passport} = require('../../../pageobjects/Passport.js');
const {EditCounterPage} = require('../../../pageobjects/EditCounterPage');
const {CreateCounterPage} = require('../../../pageobjects/CreateCounterPage');
const {simpleUser: user} = require('../../../data/users');
const grantsData = require('../../../data/counterGransData');

beforeEach(function () {
    return new Passport(this.browser).login(user);
});

describe('Выдача доступа', function () {
    let page;
    let counterId;

    beforeEach(async function () {
        const createPage = new CreateCounterPage(this.browser);
        await createPage.open();
        counterId = await createPage.createCounter();

        page = await new EditCounterPage(this.browser);
        await page.openGrants(counterId);
    });

    describe('Проверка логинов:', function () {
        const testUsers = [
            {
                description: 'Обычный пользователь',
                grantUserLogin: grantsData.simpleUser.realLogin,
                expectedGrantUserLogin: grantsData.simpleUser.expectedLogin
            },
            {
                description: 'Адрес яндекс почты',
                grantUserLogin: grantsData.yandexMailUser.realLogin,
                expectedGrantUserLogin: grantsData.yandexMailUser.expectedLogin
            },
            {
                description: 'Простой lite-пользователь',
                grantUserLogin: grantsData.liteUser.realLogin,
                expectedGrantUserLogin: grantsData.liteUser.expectedLogin
            },
            {
                description: 'Дозарегестрированный lite-пользователь',
                grantUserLogin: grantsData.registeredLiteUser.realLogin,
                expectedGrantUserLogin: grantsData.registeredLiteUser.expectedLogin
            },
            {
                description: 'ПДД',
                grantUserLogin: grantsData.pddUser.realLogin,
                expectedGrantUserLogin: grantsData.pddUser.expectedLogin
            },
            {
                description: 'Номер телефона',
                grantUserLogin: grantsData.phoneNumberUser.realLogin,
                expectedGrantUserLogin: grantsData.phoneNumberUser.expectedLogin
            },
        ];

        testUsers.forEach(function (testUser) {
            it(`${testUser.description}`, async function () {
                await page.createGrant(testUser.grantUserLogin, false);
                await page.refresh();
                const grants = await page.getAllGrants();
                assert.include(grants, testUser.expectedGrantUserLogin, 'пользователь присутствует в доступах');
            });
        });
    });

    describe('Проверка права доступа:', function () {
        const permissionTypes = [
            {type: 'Только просмотр', isEdit: false},
            {type: 'Редактирование', isEdit: true}
        ];

        permissionTypes.forEach(function (permissionType) {
            it(`${permissionType.type}`, async function () {
                await page.createGrant(grantsData.simpleUser.realLogin, permissionType.isEdit);
                await page.refresh();
                const grantsPermission = await page.getGrantPermission();
                assert.equal(grantsPermission, permissionType.type, 'права совпадают с ожидаемыми');
            });
        });
    });

    afterEach(async function () {
        await page.deleteCounter(counterId);
    });
});
