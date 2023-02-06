import { assert } from 'chai';
import { ItCallback } from 'hermione';
import { Passport } from 'tests/pageObjects/Passport';
import { CampaignSettings } from 'tests/pageObjects/CampaignSettings';

import { getNewLanding } from 'tests/apiHelpers/landings';
import { createCounter, deleteCounterById } from 'tests/apiHelpers/counters';
import {
    createAdvertiserWithName,
    deleteAdvertiserByName,
} from 'tests/apiHelpers/advertiser';
import {
    deleteCampaignByName,
    createCampaign,
} from 'tests/apiHelpers/campaign';
import { GoalToSave } from 'tests/externalServices/metrika/types';
import { getRandomName } from 'tests/utils/random';

const createGoal = (name: string): GoalToSave => ({
    name,
    depth: 3,
    flag: 'basket',
    type: 'number',
    conditions: {
        type: 'contain',
        url: '/test',
    },
    is_retargeting: 0,
});

beforeEach(async function(this: ItCallback) {
    const passport = new Passport(this.browser);

    const advertiserName = getRandomName(15);
    const advertiser = await createAdvertiserWithName(advertiserName);
    await this.browser.setMeta('advertiserId', advertiser.advertiserId);

    const landing = await getNewLanding(advertiser.advertiserId);

    const campaignName = getRandomName(50);
    const campaign = await createCampaign({
        advertiserId: advertiser.advertiserId,
        landingId: landing.landingId,
        name: campaignName,
    });

    await this.browser.setMeta('campaignName', campaign.name);
    await this.browser.setMeta('campaignId', campaign.campaignId);

    await passport.login(hermione.ctx.user);
});

describe('Редактирование кампании без целей', () => {
    it('должен изменить описание', async function(this: ItCallback) {
        const page = new CampaignSettings(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');
        const campaignId = await this.browser.getMeta('campaignId');

        await page.descriptionPage.open(advertiserId, campaignId);
        await page.descriptionPage.waitForLoad();

        const campaignName = page.descriptionPage.createAllowedName();
        await page.descriptionPage.nameInput.setValue(campaignName);
        await this.browser.setMeta('campaignName', campaignName);

        await page.descriptionPage.calendar.selectPeriod(3, 5);

        const valuesBeforeSave = await page.descriptionPage.collectValues();

        await page.saveChanges();
        await this.browser.refresh();
        await page.descriptionPage.waitForLoad();

        const valuesAfterRefresh = await page.descriptionPage.collectValues();

        assert.deepEqual(
            valuesAfterRefresh,
            valuesBeforeSave,
            'изменения не сохранились',
        );
    });

    it('должен изменить плановые показатели', async function(this: ItCallback) {
        const page = new CampaignSettings(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');
        const campaignId = await this.browser.getMeta('campaignId');

        await page.planPage.open(advertiserId, campaignId);
        await page.planPage.waitForLoad();

        await page.planPage.clearCommonPlan();
        await page.planPage.fillCommonPlan();

        const valuesBeforeSave = await page.planPage.collectCommonPlan();

        await page.saveChanges();
        await this.browser.refresh();
        await page.planPage.waitForLoad();

        const valuesAfterRefresh = await page.planPage.collectCommonPlan();

        assert.deepEqual(
            valuesAfterRefresh,
            valuesBeforeSave,
            'изменения не сохранились',
        );
    });
});

describe('Редактирование кампании с целями', () => {
    beforeEach(async function(this: ItCallback) {
        const goalName = getRandomName(15);

        const counter = await createCounter('test13.com', [
            createGoal(goalName),
        ]);

        await this.browser.setMeta('counterId', counter.id);
        await this.browser.setMeta('goalName', goalName);
    });

    it('должен изменить привязанные цели и плановые показатели', async function(this: ItCallback) {
        const page = new CampaignSettings(this.browser);
        const advertiserId = await this.browser.getMeta('advertiserId');
        const campaignId = await this.browser.getMeta('campaignId');
        const goalName = await this.browser.getMeta('goalName');

        await page.goalsPage.open(advertiserId, campaignId);

        await page.goalsPage.waitForLoad();

        await page.goalsPage.select.selectName(goalName);

        await page.saveChanges();

        await page.planPage.open(advertiserId, campaignId);
        await page.planPage.waitForLoad();

        await page.planPage.clearCommonPlan();
        await page.planPage.fillFullForm(goalName);

        const valuesBeforeSave = await page.planPage.collectCommonPlan();

        await page.saveChanges();
        await this.browser.refresh();
        await page.planPage.waitForLoad();

        const valuesAfterRefresh = await page.planPage.collectCommonPlan();

        assert.deepEqual(
            valuesAfterRefresh,
            valuesBeforeSave,
            'изменения не сохранились',
        );
    });

    afterEach(async function(this: ItCallback) {
        const id = await this.browser.getMeta('counterId');

        await deleteCounterById(id);
    });
});

afterEach(async function(this: ItCallback) {
    const name = await this.browser.getMeta('advertiserName');
    const campaignName = await this.browser.getMeta('campaignName');

    await deleteAdvertiserByName(name);
    await deleteCampaignByName(campaignName);
});
