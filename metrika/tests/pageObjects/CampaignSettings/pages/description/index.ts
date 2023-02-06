import { Page } from 'tests/pageObjects/Page';
import { createIdSelector, testIds } from 'shared/testIds';
import { DatePicker } from 'tests/pageObjects/DatePicker';
import { SearchSelect } from 'tests/pageObjects/SearchSelect';
import { Browser } from 'hermione';
import { Chance } from 'chance';

const chance = new Chance();

class DescriptionPage extends Page {
    calendar: DatePicker;
    advertiserSelect: SearchSelect;

    constructor(browser: Browser) {
        super(browser);

        this.calendar = new DatePicker(this.browser);
        this.advertiserSelect = new SearchSelect(this.browser);
    }

    createAllowedName() {
        const length = chance.natural({ min: 2, max: 256 });
        return chance.string({ length });
    }

    get nameInput() {
        return this.browser.$(
            createIdSelector(testIds.campaign.edit.description.name),
        );
    }

    async collectValues() {
        return {
            name: await this.nameInput.getValue(),
            date: await this.calendar.button.getText(),
            advertiser: await this.advertiserSelect.input.getValue(),
        };
    }

    open(advertiserId: number, campaignId: number) {
        return this.browser.url(
            `/advertiser/${advertiserId}/campaign/${campaignId}/edit/common`,
        );
    }

    waitForLoad() {
        return this.nameInput.customWaitForExist();
    }
}

export { DescriptionPage };
