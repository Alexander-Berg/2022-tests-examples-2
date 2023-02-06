import { Page } from '../Page';
import { testIds, createClassSelector } from 'shared/testIds';

class ConfirmModal extends Page {
    get confirmButton() {
        return this.browser.$(
            createClassSelector(testIds.common.modal.confirm),
        );
    }

    async confirm() {
        await this.confirmButton.click();
        await this.confirmButton.customWaitForExist({ reverse: true });
    }
}

export { ConfirmModal };
