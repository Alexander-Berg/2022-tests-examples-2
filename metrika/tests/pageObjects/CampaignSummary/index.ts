import { Browser } from 'hermione';
import { Page } from '../Page';
import { createClassSelector, testIds, helpSelectors } from 'shared/testIds';
import { ConfirmModal } from 'tests/pageObjects/ConfirmModal';

class CampaignSummary extends Page {
    confirmModal: ConfirmModal;

    constructor(browser: Browser) {
        super(browser);

        this.confirmModal = new ConfirmModal(browser);
    }

    get menuButton() {
        return this.browser.$(
            `${createClassSelector(testIds.campaign.summary.menu)} ${
                helpSelectors.lego.button
            }`,
        );
    }

    get statusToggler() {
        return this.browser.$(
            createClassSelector(testIds.campaign.summary.statusToggler),
        );
    }

    get deleteButton() {
        return this.browser.$(
            createClassSelector(testIds.campaign.summary.delete),
        );
    }

    async archiveCampaign() {
        await this.menuButton.click();
        await this.statusToggler.click();
    }

    async activateCampaign() {
        await this.menuButton.click();
        await this.statusToggler.click();
    }

    async deleteCampaign() {
        await this.menuButton.click();
        await this.deleteButton.click();

        await this.confirmModal.confirm();
    }

    open(advertiserId: number, campaignId: number) {
        return this.browser.url(
            `/advertiser/${advertiserId}/campaign/${campaignId}`,
        );
    }
}

export { CampaignSummary };
