import { Browser } from 'hermione';
import { testIds, createClassSelector } from 'shared/testIds';

class Page {
    browser: Browser;

    constructor(browser: Browser) {
        this.browser = browser;
    }

    get spinner() {
        return this.browser.$(createClassSelector(testIds.common.spinner));
    }

    waitForLoad() {
        return this.spinner.customWaitForExist({
            reverse: true,
            milliseconds: 3000,
        });
    }
}

export { Page };
