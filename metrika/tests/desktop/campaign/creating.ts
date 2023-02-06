import { ItCallback } from 'hermione';
import { Passport } from 'tests/pageObjects/Passport';
import { CampaignSettings } from 'tests/pageObjects/CampaignSettings';

import { createCounter, deleteCounterById } from 'tests/apiHelpers/counters';
import {
    createAdvertiserWithName,
    deleteAdvertiserByName,
} from 'tests/apiHelpers/advertiser';
import { deleteCampaignByName } from 'tests/apiHelpers/campaign';
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

    await this.browser.setMeta('advertiserName', advertiser.name);

    await passport.login(hermione.ctx.user);
});

describe('Создание кампании с целями', () => {
    beforeEach(async function(this: ItCallback) {
        const goalName = getRandomName(30);

        const counter = await createCounter('test13.com', [
            createGoal(goalName),
        ]);

        await this.browser.setMeta('counterId', counter.id);
        await this.browser.setMeta('goalName', goalName);
    });

    it('должен создаться новая кампания', async function(this: ItCallback) {
        const page = new CampaignSettings(this.browser);

        await page.open();

        const campaignName = page.descriptionPage.createAllowedName();
        await page.descriptionPage.nameInput.setValue(campaignName);
        await this.browser.setMeta('campaignName', campaignName);

        await page.descriptionPage.calendar.selectPeriod(1, 2);

        const advertiserName = await this.browser.getMeta('advertiserName');
        await page.descriptionPage.advertiserSelect.selectName(advertiserName);

        await page.nextButton.click();

        const goalName = await this.browser.getMeta('goalName');
        await page.goalsPage.waitForLoad();
        await page.goalsPage.select.selectName(goalName);

        await page.nextButton.click();

        await page.planPage.fillFullForm(goalName);

        await page.nextButton.click();

        await page.placementsPage.createPlacement();

        await page.nextButton.click();
    });

    afterEach(async function(this: ItCallback) {
        const id = await this.browser.getMeta('counterId');

        await deleteCounterById(id);
    });
});

describe('Создание кампании без целей', () => {
    it('должен создаться новая кампания', async function(this: ItCallback) {
        const page = new CampaignSettings(this.browser);

        await page.open();

        const campaignName = page.descriptionPage.createAllowedName();
        await page.descriptionPage.nameInput.setValue(campaignName);
        await this.browser.setMeta('campaignName', campaignName);

        await page.descriptionPage.calendar.selectPeriod(1, 2);

        const advertiserName = await this.browser.getMeta('advertiserName');
        await page.descriptionPage.advertiserSelect.selectName(advertiserName);

        await page.nextButton.click();

        await page.nextButton.click();

        await page.planPage.fillCommonPlan();

        await page.nextButton.click();

        await page.placementsPage.createPlacement();

        await page.nextButton.click();
    });
});

afterEach(async function(this: ItCallback) {
    const name = await this.browser.getMeta('advertiserName');
    const campaignName = await this.browser.getMeta('campaignName');

    await deleteAdvertiserByName(name);
    await deleteCampaignByName(campaignName);
});
