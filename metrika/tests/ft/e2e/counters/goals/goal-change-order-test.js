'use strict'

const { assert } = require('chai');
const { Passport } = require('../../../pageobjects/Passport.js');
const { EditCounterPage } = require('../../../pageobjects/EditCounterPage');
const { simpleUser: user } = require('../../../data/users');
const { goalOrderTestCounter: counter } = require('../../../data/counters');

beforeEach(function() {
    return new Passport(this.browser).login(user);
});

describe('Порядок целей счетчика', function() {
    let page;

    beforeEach(function() {
        page = new EditCounterPage(this.browser);
        page.openGoals(counter.id);
    })

    it('Изменение порядка целей', async function() {
        const oldGoals = await page.getGoalIds();
        await page.changeGoalsOrder();
        const currentGoals = await page.getGoalIds();

        assert.notSameOrderedMembers(currentGoals, oldGoals, 'подрядок целей изменен');
    });
});
