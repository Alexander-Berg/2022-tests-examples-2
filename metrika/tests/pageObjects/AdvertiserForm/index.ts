import { Page } from '../Page';
import { Chance } from 'chance';
import { createIdSelector, testIds } from 'shared/testIds';

const chance = new Chance();

class AdvertiserForm extends Page {
    get nameInput() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.nameInput),
        );
    }

    get postClickDaysInput() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.postClickInput),
        );
    }

    get postViewDaysInput() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.postViewInput),
        );
    }

    get advertiserSaveError() {
        return this.browser.$(createIdSelector(testIds.advertiser.form.error));
    }

    get saveAdvertiserButton() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.saveButton),
        );
    }

    get changeWarning() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.changeWarning),
        );
    }

    get deleteButton() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.deleteButton),
        );
    }

    get confirmDeleteButton() {
        return this.browser.$(
            createIdSelector(testIds.advertiser.form.confirmDelete),
        );
    }

    open(id?: string) {
        return id
            ? this.browser.url(`/advertiser/${id}/edit/common`)
            : this.browser.url('/advertiser/new');
    }

    unfocusForm() {
        return this.browser.click('body');
    }

    submit() {
        return this.saveAdvertiserButton.click();
    }

    checkError() {
        this.advertiserSaveError.customWaitForExist().then(
            () => {
                throw new Error('ошибка не должна была появиться');
            },
            () => {
                return true;
            },
        );
    }

    async fillFormWithRandomValues() {
        const name = AdvertiserForm.createAllowedName();
        await this.browser.setMeta('name', name);
        await this.nameInput.setValue(name);

        const postClickDays = AdvertiserForm.createAllowedPostClickDays();
        await this.browser.setMeta('postClickDays', postClickDays);
        await this.postClickDaysInput.setValue(postClickDays);

        const postViewDays = AdvertiserForm.createAllowedPostViewDays();
        await this.browser.setMeta('postViewDays', postViewDays);
        await this.postViewDaysInput.setValue(postViewDays);
    }

    static createAllowedName() {
        const length = chance.natural({ min: 2, max: 256 });
        return chance.string({ length });
    }

    static createAllowedPostClickDays() {
        return chance.natural({ min: 1, max: 30 });
    }

    static createAllowedPostViewDays() {
        return chance.natural({ min: 1, max: 90 });
    }
}

export { AdvertiserForm };
