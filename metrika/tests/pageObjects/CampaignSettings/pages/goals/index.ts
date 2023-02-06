import { Browser } from 'hermione';
import { Page } from 'tests/pageObjects/Page';
import { BaseSelect } from 'tests/pageObjects/BaseSelect';

class GoalsPage extends Page {
    select: BaseSelect;

    constructor(browser: Browser) {
        super(browser);

        this.select = new BaseSelect(this.browser);
    }

    open(advertiserId: number, campaignId: number) {
        return this.browser.url(
            `/advertiser/${advertiserId}/campaign/${campaignId}/edit/goals`,
        );
    }

    waitForLoad() {
        return this.select.button.customWaitForExist();
    }
}

export { GoalsPage };
