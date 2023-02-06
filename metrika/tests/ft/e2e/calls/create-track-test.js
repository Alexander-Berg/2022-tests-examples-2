'use strict'

const { assert } = require('chai');
const { Passport } = require('../../pageobjects/Passport.js');
const { CallsPage } = require('../../pageobjects/CallsPage');
const { simpleUser: user } = require('../../data/users');

beforeEach(function() {
    return new Passport(this.browser).login(user);
});

describe('Создание номера ЦЗ', function() {
    let page;

    beforeEach(async function() {
        page = new CallsPage(this.browser);
        await page.open();
    });

    it('Номер присутствует в списке', async function() {
        const oldTracks = await page.countTracks();
        await page.createTrack();
        await page.refresh();
        const newTracks = await page.countTracks();
        assert.isAbove(newTracks, oldTracks, 'новый трек-номер добавлен')

    });

    afterEach(async function() {
        await page.removeAllTracks();
    });
});
