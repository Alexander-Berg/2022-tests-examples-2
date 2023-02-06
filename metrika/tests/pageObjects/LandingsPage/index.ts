import { Page } from '../Page';
import {
    createIdSelector,
    testIds,
    createXPathIdSelector,
} from 'shared/testIds';

const nameXPathIdSelector = createXPathIdSelector(
    testIds.landings.page.landingName,
);
const editButtonXPathIdSelector = createXPathIdSelector(
    testIds.landings.page.editButton,
);

class LandingsPage extends Page {
    get createButton() {
        return this.browser.$(
            createIdSelector(testIds.landings.page.createButton),
        );
    }

    get name() {
        return this.browser.$(
            createIdSelector(testIds.landings.page.landingName),
        );
    }

    hasLandingWithName(name: string) {
        return this.browser.isExisting(
            `.//*[${nameXPathIdSelector} and text()="${name}"]`,
        );
    }

    getLandingWithName(name: string) {
        return this.browser.$(
            `.//*[${nameXPathIdSelector} and text()="${name}"]`,
        );
    }

    getEditButton(name: string) {
        return this.getLandingWithName(name).$(
            `./ancestor::*//*[${editButtonXPathIdSelector}]`,
        );
    }

    open(advertiserId: string) {
        return this.browser.url(`/advertiser/${advertiserId}/edit/landings`);
    }
}

export { LandingsPage };
