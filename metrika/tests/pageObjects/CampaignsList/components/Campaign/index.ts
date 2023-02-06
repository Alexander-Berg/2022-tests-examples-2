import { Page } from 'tests/pageObjects/Page';
import {
    testIds,
    createClassSelector,
    createXPathIdSelector,
} from 'shared/testIds';

const menuXPathSelector = createXPathIdSelector(
    testIds.campaigns.item.menuButton,
);
const rowXPathSelector = createXPathIdSelector(testIds.campaigns.item.row);

const findWithContext = (context: string, searchXPath: string) =>
    `.//*[${rowXPathSelector}]//*[text()="${context}"]/ancestor::*[${rowXPathSelector}]//*[${searchXPath}]`;

class Campaign extends Page {
    getMenuButton(context: string) {
        return this.browser.$(findWithContext(context, menuXPathSelector));
    }

    getCopyButton() {
        return this.browser.$(createClassSelector(testIds.campaigns.item.copy));
    }

    getName(name: string) {
        return this.browser.$(`.//*[${rowXPathSelector}]//*[text()="${name}"]`);
    }
}

export { Campaign };
