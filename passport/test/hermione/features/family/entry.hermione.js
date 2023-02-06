const expect = require('chai').expect;
const {TEST_ID} = require('../../const');
const pages = require('../../utils/passportPages');
const PageObjects = require('../../page-objects/family');

hermione.skip.in('edge-desktop', 'На скринах видно что пользователя не залогинило.');
describe('Family open entry', function() {
    const layout = PageObjects.layout();
    const mainLayout = PageObjects.layout.main();
    const inviteLayout = PageObjects.layout.invite();
    const redesignInvite = PageObjects.layout.redesignInvite();
    const errorLayout = PageObjects.layout.error();
    const payLimits = PageObjects.payLimits();

    const layouts = [mainLayout, inviteLayout, redesignInvite, errorLayout];

    const checkLayoutIsShowed = async (layout, browser) =>
        Promise.all(
            layouts.map(async (curLayout) => {
                if (layout === curLayout) {
                    await browser.waitForExist(curLayout);
                    expect(await browser.isExisting(curLayout)).to.equal(true);
                } else {
                    expect(await browser.isExisting(curLayout)).to.equal(false);
                }
            })
        );

    beforeEach(async function() {
        await this.browser.auth('yndx-family-hermione');
        await this.browser.yaSetTestId([TEST_ID.FAMILY_PAY, TEST_ID.FAMILY_PAY_3DS]);
    });

    afterEach(async function() {
        await this.browser.yaSetTestId([]);
    });

    it('main', async function() {
        await this.browser.url(pages.FAMILY_MAIN.getUrl());
        await this.browser.waitForExist(layout);

        await checkLayoutIsShowed(mainLayout, this.browser);
    });

    it('invite create', async function() {
        await this.browser.url(pages.FAMILY_INVITE.getUrl());
        await this.browser.waitForExist(layout);

        await checkLayoutIsShowed(redesignInvite, this.browser);
    });

    it('invite confirm', async function() {
        await this.browser.url(
            pages.FAMILY_INVITE_CONFIRM.getUrl().replace('$inviteId', '10d7e7f6-88f6-4299-a653-c8f5e1d81e3f')
        );
        await this.browser.waitForExist(layout);

        await checkLayoutIsShowed(inviteLayout, this.browser);
    });

    it('error', async function() {
        await this.browser.url(
            pages.FAMILY_INVITE_CONFIRM.getUrl().replace('$inviteId', 'ololololololololololololololololololololo')
        );
        await this.browser.waitForExist(layout);

        await checkLayoutIsShowed(errorLayout, this.browser);
    });

    hermione.skip.in(/.*/, 'Нужно научится заходить с нужной кукой.');
    it('limits', async function() {
        await this.browser.url(pages.FAMILY_PAY_LIMITS.getUrl());
        await this.browser.waitForExist(layout);

        await this.browser.waitForExist(payLimits);
        expect(await this.browser.isExisting(payLimits)).to.equal(true);
    });
});
