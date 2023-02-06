'use strict'

const {assert} = require('chai');
const {Passport} = require('../../../pageobjects/Passport.js');
const {EditCounterPage} = require('../../../pageobjects/EditCounterPage');
const {simpleUser: user} = require('../../../data/users');
const {goalCreateTestCounter: counter} = require('../../../data/counters');

beforeEach(function () {
    return new Passport(this.browser).login(user);
});

describe('Создание целей', function () {
    let page;
    let oldGoals;

    beforeEach(async function () {
        page = new EditCounterPage(this.browser);
        await page.openGoals(counter.id);

        oldGoals = await page.countGoals();
    })

    it('Добавление url цели', async function () {
        await page.createUrlGoal(false);

        const goalList = await page.countGoals();

        assert.isAbove(goalList, oldGoals, 'цель добавлена');
    });

    it('Добавление ретаргетинг url цели', async function () {
        await page.createUrlGoal(true)

        const goalList = await page.countGoals();

        assert.isAbove(goalList, oldGoals, 'цель добавлена');
    });

    it('Добавление составной цели', async function () {
        await page.createCompositeGoal(false);

        const goalList = await page.countGoals();

        assert.isAbove(goalList, oldGoals, 'цель добавлена');
    });

    it('Добавление ретаргетинг составной цели', async function () {
        await page.createCompositeGoal(true);

        const goalList = await page.countGoals();

        assert.isAbove(goalList, oldGoals, 'цель добавлена');
    });

});
