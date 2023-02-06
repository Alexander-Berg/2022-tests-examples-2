import { Page } from '../Page';
import { Chance } from 'chance';
import { createIdSelector, testIds } from 'shared/testIds';

const chance = new Chance();

class LandingsEditForm extends Page {
    get nameInput() {
        return this.browser.$(
            createIdSelector(testIds.landings.form.nameInput),
        );
    }

    get urlInput() {
        return this.browser.$(createIdSelector(testIds.landings.form.urlInput));
    }

    get saveButton() {
        return this.browser.$(
            createIdSelector(testIds.landings.form.saveButton),
        );
    }

    get deleteButton() {
        return this.browser.$(
            createIdSelector(testIds.landings.form.deleteButton),
        );
    }

    get confirmDeleteButton() {
        return this.browser.$(
            createIdSelector(testIds.landings.form.confirmDeleteButton),
        );
    }

    async fillFormWithRandomValues() {
        const name = LandingsEditForm.createAllowedName();
        await this.nameInput.customClearValue();
        await this.nameInput.setValue(name);
        await this.browser.setMeta('newName', name);

        const url = LandingsEditForm.createAllowedUrl();
        await this.urlInput.customClearValue();
        await this.urlInput.setValue(url);
        return this.browser.setMeta('URL', url);
    }

    static createAllowedName() {
        const length = chance.natural({ min: 2, max: 256 });
        return chance.string({ length });
    }

    static createAllowedUrl() {
        return chance.url({ protocol: 'https' });
    }

    async saveAndClose() {
        await this.saveButton.customWaitForEnabled();
        await this.saveButton.click();
        return this.saveButton.customWaitForExist({
            milliseconds: 5000,
            reverse: true,
        });
    }

    async deleteAndClose() {
        await this.deleteButton.click();

        await this.confirmDeleteButton.customWaitForExist();
        await this.confirmDeleteButton.click();

        return this.deleteButton.customWaitForExist({
            milliseconds: 5000,
            reverse: true,
        });
    }
}

export { LandingsEditForm };
