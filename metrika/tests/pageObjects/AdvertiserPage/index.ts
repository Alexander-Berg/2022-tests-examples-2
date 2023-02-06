import { Page } from '../Page';
import { createIdSelector, testIds, createClassSelector } from 'shared/testIds';

class AdvertiserPage extends Page {
    get advertiserName() {
        return this.browser.$(createIdSelector(testIds.advertiser.page.name));
    }

    get menuButton() {
        return this.browser.$(
            createClassSelector(testIds.advertiser.page.headerMenu),
        );
    }

    get rejectGrantButton() {
        return this.browser.$(
            createClassSelector(testIds.advertiser.page.rejectAccess),
        );
    }

    get deleteAdvertiserButton() {
        return this.browser.$(
            createClassSelector(testIds.advertiser.page.deleteAdvertiser),
        );
    }

    get confirmDeleteButton() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.page.confirmDelete),
        );
    }

    get campaignsTableSpinner() {
        return this.browser.$(
            createClassSelector(testIds.campaigns.table.spinner),
        );
    }

    open(id: string) {
        return this.browser.url(`/advertiser/${id}`);
    }

    waitFetchData() {
        return this.campaignsTableSpinner.customWaitForExist({
            reverse: true,
            milliseconds: 5000,
        });
    }
}

export { AdvertiserPage };
