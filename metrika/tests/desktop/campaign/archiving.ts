import { assert } from 'chai';
import { ItCallback } from 'hermione';
import { Passport } from 'tests/pageObjects/Passport';
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

    const campaignName = getRandomName(50);
    const landing = await getNewLanding(advertiser.advertiserId);
    const campaign = await createCampaign({
        advertiserId: advertiser.advertiserId,
        landingId: landing.landingId,
        name: campaignName,
    });

    await this.browser.setMeta('campaignName', campaign.name);
    await this.browser.setMeta('campaignId', campaign.campaignId);

    await passport.login(hermione.ctx.user);
});

describe('Архивирование кампании', () => {
    it('должна архивироваться и активироваться кампания', async function(this: ItCallback) {
        const list = new CampaignsList(this.browser);
        const summary = new CampaignSummary(this.browser);
        const campaignName = await this.browser.getMeta('campaignName');
        const advertiserId = await this.browser.getMeta('advertiserId');
        const campaignId = await this.browser.getMeta('campaignId');

        await summary.open(advertiserId, campaignId);
        await summary.waitForLoad();

        await summary.archiveCampaign();

        await list.open();
        await list.waitForLoad();
        await list.selectStatus('archived');
        await list.waitForLoad();
        const isArchived = await list.checkCampaignExistance(campaignName);
        assert.isTrue(isArchived);

        await summary.open(advertiserId, campaignId);
        await summary.waitForLoad();

        await summary.activateCampaign();

        await list.open();
        await list.waitForLoad();
        await list.selectStatus('active');
        await list.waitForLoad();
        const isActive = await list.checkCampaignExistance(campaignName);
        assert.isTrue(isActive);
    });
});

afterEach(async function(this: ItCallback) {
    const advertiserId = await this.browser.getMeta('advertiserId');
    const campaignName = await this.browser.getMeta('campaignName');

    await deleteAdvertiserById(advertiserId);
    await deleteCampaignByName(campaignName);
});
