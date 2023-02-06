import { assert } from 'chai';
import { ItCallback } from 'hermione';
import { Passport } from 'tests/pageObjects/Passport';
import { CampaignSettings } from 'tests/pageObjects/CampaignSettings';
import { CampaignSummary } from 'tests/pageObjects/CampaignSummary';
import { CampaignsList } from 'tests/pageObjects/CampaignsList';

import {
    createAdvertiserWithName,
    deleteAdvertiserById,
} from 'tests/apiHelpers/advertiser';
import { getNewLanding } from 'tests/apiHelpers/landings';
import {
    deleteCampaignByName,
    createCampaign,
} from 'tests/apiHelpers/campaign';
import { getRandomName } from 'tests/utils/random';

beforeEach(async function(this: ItCallback) {
    const passport = new Passport(this.browser);

    const advertiserName = getRandomName(15);
    const advertiser = await createAdvertiserWithName(advertiserName);
    await this.browser.setMeta('advertiserId', advertiser.advertiserId);

    const landing = await getNewLanding(advertiser.advertiserId);
    await this.browser.setMeta('landingId', landing.landingId);

    await passport.login(hermione.ctx.user);
});

describe('Удаление кампании', () => {
    beforeEach(async function(this: ItCallback) {
        const advertiserId = await this.browser.getMeta('advertiserId');
        const landingId = await this.browser.getMeta('landingId');

        const campaignName = getRandomName(50);
        const campaign = await createCampaign({
            advertiserId,
            landingId,
            name: campaignName,
        });

        await this.browser.setMeta('campaignName', campaign.name);
        await this.browser.setMeta('campaignId', campaign.campaignId);
    });

    it('должна удалиться со страницы страницы сводки', async function(this: ItCallback) {
        const list = new CampaignsList(this.browser);
        const summary = new CampaignSummary(this.browser);
        const campaignName = await this.browser.getMeta('campaignName');
        const advertiserId = await this.browser.getMeta('advertiserId');
        const campaignId = await this.browser.getMeta('campaignId');

        await summary.open(advertiserId, campaignId);
        await summary.waitForLoad();

        await summary.deleteCampaign();

        await list.waitForLoad();
        const isExisting = await list.checkCampaignExistance(campaignName);
        assert.isFalse(isExisting);
    });

    it('должна удалиться со страницы настройки кампании', async function(this: ItCallback) {
        const list = new CampaignsList(this.browser);
        const settings = new CampaignSettings(this.browser);
        const campaignName = await this.browser.getMeta('campaignName');
        const advertiserId = await this.browser.getMeta('advertiserId');
        const campaignId = await this.browser.getMeta('campaignId');

        await settings.descriptionPage.open(advertiserId, campaignId);
        await settings.descriptionPage.waitForLoad();

        await settings.deleteCampaign();

        await list.waitForLoad();
        const isExisting = await list.checkCampaignExistance(campaignName);
        assert.isFalse(isExisting);
    });

    afterEach(async function(this: ItCallback) {
        const campaignName = await this.browser.getMeta('campaignName');

        try {
            await deleteCampaignByName(campaignName);
        } catch (error) {}
    });
});

afterEach(async function(this: ItCallback) {
    const advertiserId = await this.browser.getMeta('advertiserId');

    await deleteAdvertiserById(advertiserId);
});
