import { assert } from 'chai';
import { ItCallback } from 'hermione';
import { AdvertiserForm } from 'tests/pageObjects/AdvertiserForm';
import { Passport } from 'tests/pageObjects/Passport';
import {
    deleteAdvertiserById,
    deleteAdvertiserByName,
    getNewAdvertiseId,
} from 'tests/apiHelpers/advertiser';
import { AdvertiserPage } from 'tests/pageObjects/AdvertiserPage';

beforeEach(async function(this: ItCallback) {
    const passport = new Passport(this.browser);

    return passport.login(hermione.ctx.user);
});

describe('Создание рекламодателя', () => {
    it('должен создаться новый рекламодатель', async function(this: ItCallback) {
        const form = new AdvertiserForm(this.browser);

        await form.open();

        await form.fillFormWithRandomValues();
        const name = await this.browser.getMeta('name');

        await form.unfocusForm();
        await form.submit();

        return this.browser
            .customWaitForRedirect({ timeout: 1000 })
            .then(() => {
                return deleteAdvertiserByName(name);
            });
    });

    it('должна нарисоваться правильная верстка', async function(this: ItCallback) {
        const form = new AdvertiserForm(this.browser);

        await form.open();

        return this.browser.assertView('plain', 'body');
    });
});

describe('Изменение рекламодателя', () => {
    beforeEach(async function(this: ItCallback) {
        const id = await getNewAdvertiseId();

        this.browser.setMeta('id', id);
    });

    it('должен измениться существующий рекламодатель', async function(this: ItCallback) {
        const form = new AdvertiserForm(this.browser);
        const id = await this.browser.getMeta('id');

        await form.open(id);
        await form.waitForLoad();

        await form.fillFormWithRandomValues();
        const name = await this.browser.getMeta('name');

        const visible = await form.changeWarning.isVisible();
        assert.isOk(visible);

        await form.unfocusForm();

        await form.submit();
        await form.checkError();

        const page = new AdvertiserPage(this.browser);
        await page.open(id);

        await page.waitForLoad();

        const text = await page.advertiserName.getText();
        assert.include(text, name);
    });

    it('рекламодатель должен удалиться через главную страницу', async function(this: ItCallback) {
        const page = new AdvertiserPage(this.browser);
        const id = await this.browser.getMeta('id');

        await page.open(id);
        await page.waitForLoad();

        await page.menuButton.click();
        const isDisabled = await page.rejectGrantButton.customIsElementDisabled();

        if (!isDisabled) {
            throw new Error('кнопка должна быть не активна');
        }

        await page.deleteAdvertiserButton.click();
        const url = await this.browser.getUrl();
        await page.confirmDeleteButton.click();

        return this.browser.customWaitForRedirect({ url });
    });

    it('рекламодатель должен удалиться через страницу настроек', async function(this: ItCallback) {
        const form = new AdvertiserForm(this.browser);
        const id = await this.browser.getMeta('id');

        await form.open(id);
        await form.waitForLoad();

        await form.deleteButton.click();
        const url = await this.browser.getUrl();
        await form.confirmDeleteButton.click();

        return this.browser.customWaitForRedirect({ url });
    });

    it('должна нарисоваться правильная верстка для страницы рекламодателя', async function(this: ItCallback) {
        const page = new AdvertiserPage(this.browser);
        const id = await this.browser.getMeta('id');

        await page.open(id);

        await page.waitForLoad();
        await page.waitFetchData();

        return this.browser.assertView('plain', 'body');
    });

    it('должна нарисоваться правильная верстка для страницы настроек', async function(this: ItCallback) {
        const form = new AdvertiserForm(this.browser);
        const id = await this.browser.getMeta('id');

        await form.open(id);

        await form.waitForLoad();

        return this.browser.assertView('plain', 'body');
    });

    afterEach(async function(this: ItCallback) {
        const id = await this.browser.getMeta('id');

        await deleteAdvertiserById(id);
    });
});
