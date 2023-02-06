import { assert } from 'chai';
import { ItCallback } from 'hermione';
import { Passport } from 'tests/pageObjects/Passport';
import {
    deleteAdvertiserById,
    getNewAdvertiseId,
} from 'tests/apiHelpers/advertiser';
import { getNewLanding } from 'tests/apiHelpers/landings';
import { LandingsPage } from 'tests/pageObjects/LandingsPage';
import { LandingsEditForm } from 'tests/pageObjects/LandingEditForm';

beforeEach(async function(this: ItCallback) {
    const passport = new Passport(this.browser);
    await passport.login(hermione.ctx.user);

    const id = await getNewAdvertiseId();
    this.browser.setMeta('advertiserId', id);
});

describe('Создание посадочной страницы', () => {
    it('должна создаться новая посадочная страница', async function(this: ItCallback) {
        const page = new LandingsPage(this.browser);
        const form = new LandingsEditForm(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');

        await page.open(advertiserId);
        await page.waitForLoad();

        await page.createButton.click();

        await form.fillFormWithRandomValues();
        const newName = await this.browser.getMeta('newName');

        await form.saveAndClose();

        const isExist = await page.hasLandingWithName(newName);

        assert.isOk(isExist);
    });

    it('верстка пустого списка', async function(this: ItCallback) {
        const page = new LandingsPage(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');

        await page.open(advertiserId);
        await page.waitForLoad();

        return this.browser.assertView('empty-landings-list', 'body');
    });
});

describe('Изменение посадочной страницы', () => {
    beforeEach(async function(this: ItCallback) {
        const advertiserId = await this.browser.getMeta('advertiserId');
        const landing = await getNewLanding(advertiserId);

        this.browser.setMeta('landingName', landing.name);
    });

    it('должен изменить существующую посадочную страницу', async function(this: ItCallback) {
        const page = new LandingsPage(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');
        const landingName = await this.browser.getMeta('landingName');

        await page.open(advertiserId);
        await page.getLandingWithName(landingName).customWaitForExist();
        await page.getLandingWithName(landingName).customMoveTo();

        await page.getEditButton(landingName).click();

        const form = new LandingsEditForm(this.browser);

        await form.fillFormWithRandomValues();
        const newName = await this.browser.getMeta('newName');

        await form.saveAndClose();

        const isExist = await page.hasLandingWithName(newName);

        assert.isOk(isExist);
    });

    it('должен удалить существующую посадочную страницу', async function(this: ItCallback) {
        const page = new LandingsPage(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');
        const landingName = await this.browser.getMeta('landingName');

        await page.open(advertiserId);
        await page.getLandingWithName(landingName).customWaitForExist();
        await page.getLandingWithName(landingName).customMoveTo();

        await page.getEditButton(landingName).click();

        const form = new LandingsEditForm(this.browser);

        await form.deleteAndClose();

        const isExist = await page.hasLandingWithName(landingName);

        assert.isNotOk(isExist);
    });

    it('верстка списка посадочных', async function(this: ItCallback) {
        const page = new LandingsPage(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');
        const landingName = await this.browser.getMeta('landingName');

        await page.open(advertiserId);
        await page.getLandingWithName(landingName).customWaitForExist();

        await this.browser.assertView('landings-list', 'body');

        await page.getLandingWithName(landingName).customMoveTo();
        return this.browser.assertView('landings-list-hover', 'body');
    });
});

afterEach(async function(this: ItCallback) {
    const id = await this.browser.getMeta('advertiserId');

    await deleteAdvertiserById(id);
});
