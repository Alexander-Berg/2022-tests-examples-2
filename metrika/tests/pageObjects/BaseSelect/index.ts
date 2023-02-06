import { Page } from '../Page';
import {
    testIds,
    createIdSelector,
    createXPathIdSelector,
    createClassSelector,
} from 'shared/testIds';

const contentXPathSelector = createXPathIdSelector(
    testIds.common.baseSelect.body,
);

class BaseSelect extends Page {
    get button() {
        return this.browser.$(
            createClassSelector(testIds.common.baseSelect.button),
        );
    }

    get confirmButton() {
        return this.browser.$(
            createClassSelector(testIds.common.baseSelect.confirm),
        );
    }

    get content() {
        return this.browser.$(createIdSelector(testIds.common.baseSelect.body));
    }

    getName(name: string) {
        return this.browser.$(
            `.//*[${contentXPathSelector}]//*[text()="${name}"]`,
        );
    }

    async open() {
        await this.button.click();
        return this.content.customWaitForExist();
    }

    async selectName(name: string) {
        await this.open();
        await this.getName(name).customWaitForExist();
        await this.getName(name).click();
        return this.confirmButton.click();
    }
}

export { BaseSelect };
