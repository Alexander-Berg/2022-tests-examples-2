import { Browser } from 'hermione';
import { isUndefined } from 'lodash';
import { Page } from '../Page';
import {
    createIdSelector,
    testIds,
    createXPathIdSelector,
} from 'shared/testIds';

const itemXPathIdSelector = createXPathIdSelector(
    testIds.common.searchSelect.item,
);

const inputXPathSelector = createXPathIdSelector(
    testIds.common.searchSelect.input,
);

class SearchSelect extends Page {
    context?: string;

    constructor(browser: Browser, context?: string) {
        super(browser);

        this.context = context;
    }

    get input() {
        if (isUndefined(this.context)) {
            return this.browser.$(
                createIdSelector(testIds.common.searchSelect.input),
            );
        }

        const contextXPathSelector = createXPathIdSelector(this.context);

        return this.browser.$(
            `.//*[${contextXPathSelector}]//*[${inputXPathSelector}]`,
        );
    }

    get toggler() {
        return this.browser.$(
            createIdSelector(testIds.common.searchSelect.toggler),
        );
    }

    get menu() {
        return this.browser.$(
            createIdSelector(testIds.common.searchSelect.menu),
        );
    }

    open() {
        return this.input.click();
    }

    getName(name: string) {
        return this.browser.$(
            `.//*[${itemXPathIdSelector}]//*[text()="${name}"]`,
        );
    }

    async selectName(name: string) {
        await this.open();
        await this.menu.customWaitForExist();

        await this.getName(name).customWaitForExist();

        await this.getName(name).click();
        return this.menu.customWaitForExist({ reverse: true });
    }
}

export { SearchSelect };
