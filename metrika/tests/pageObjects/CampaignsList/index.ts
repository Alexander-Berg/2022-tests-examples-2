import { Browser } from 'hermione';
import { Page } from '../Page';
import { Campaign } from './components/Campaign';
import {
    createIdSelector,
    testIds,
    createClassSelector,
    createClass,
} from 'shared/testIds';
import { ru } from 'client/components/CampaignsList/components/Toolbar/Toolbar.i18n/ru';

const statusItemCls = createClass(testIds.campaigns.status.item);

type Status = 'archived' | 'active' | 'all';

class CampaignsList extends Page {
    campaign: Campaign;

    constructor(browser: Browser) {
        super(browser);

        this.campaign = new Campaign(browser);
    }

    get tableBody() {
        return this.browser.$(createIdSelector(testIds.campaigns.table.body));
    }

    get statusButton() {
        return this.browser.$(
            createClassSelector(testIds.campaigns.status.button),
        );
    }

    getStatus(name: Status) {
        // @ts-ignore
        const text = ru[`${name}-campaigns`];
        return this.browser.$(
            `.//*[contains(@class, "${statusItemCls}")]//*[text()="${text}"]`,
        );
    }

    async selectStatus(name: Status) {
        await this.statusButton.click();

        await this.getStatus(name).click();
    }

    async copyCampaign(name: string) {
        await this.campaign.getMenuButton(name).click();
        await this.campaign.getCopyButton().click();
    }

    open(advertiserId?: number) {
        if (advertiserId) {
            return this.browser.url(`/advertiser/${advertiserId}`);
        }

        return this.browser.url('/');
    }

    checkCampaignExistance(name: string) {
        return this.campaign
            .getName(name)
            .isExisting()
            .catch(() => false);
    }

    waitForLoad() {
        return this.tableBody.customWaitForExist();
    }
}

export { CampaignsList };
