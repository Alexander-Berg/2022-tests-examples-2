import { Browser } from 'hermione';
import { Page } from 'tests/pageObjects/Page';
import { PlacementSettings } from 'tests/pageObjects/PlacementSettings';
import { testIds, createIdSelector } from 'shared/testIds';

class PlacementsPage extends Page {
    settings: PlacementSettings;

    constructor(browser: Browser) {
        super(browser);

        this.settings = new PlacementSettings(this.browser);
    }

    get createButton() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.placement.create),
        );
    }

    async createPlacement() {
        await this.createButton.click();
        await this.settings.createPlacement();
    }

    open(advertiserId: number, campaignId: number) {
        return this.browser.url(
            `/advertiser/${advertiserId}/campaign/${campaignId}/edit/placements`,
        );
    }
}

export { PlacementsPage };
