import { assert } from 'chai';
import { ItCallback } from 'hermione';
import { Passport } from 'tests/pageObjects/Passport';
import { CampaignSettings } from 'tests/pageObjects/CampaignSettings';
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
import { getRandomName, escapeRegExp } from 'tests/utils/random';

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

describe('Копирование кампании', () => {
    it('должна создаться новая кампания', async function(this: ItCallback) {
        const list = new CampaignsList(this.browser);
        const settings = new CampaignSettings(this.browser);
        const campaignName = await this.browser.getMeta('campaignName');

        await list.open();
        await list.waitForLoad();

        await list.copyCampaign(campaignName);

        await settings.descriptionPage.nameInput.customWaitForExist();
        const name = await settings.descriptionPage.nameInput.getValue();
        await this.browser.setMeta('copiedCampaignName', name);

        const regExp = new RegExp(
            `${escapeRegExp(campaignName)} \\(копия \\d+\\)`,
        );
        assert(
            regExp.test(name),
            'неправильное название скопрированной кампании',
        );

        await list.open();
        await list.waitForLoad();

        const isExist = await list.checkCampaignExistance(name);

        assert(isExist, "new campaign doesn't exist in table");
    });
});

afterEach(async function(this: ItCallback) {
    const advertiserId = await this.browser.getMeta('advertiserId');
    const campaignName = await this.browser.getMeta('campaignName');
    const copiedCampaignName = await this.browser.getMeta('copiedCampaignName');

    await deleteAdvertiserById(advertiserId);
    await deleteCampaignByName(campaignName);
    await deleteCampaignByName(copiedCampaignName);
});
