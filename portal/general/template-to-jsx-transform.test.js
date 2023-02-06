const {transformTemplateToJsx} = require('./template-to-jsx-transform');
const chai = require('chai');
const chaiJestSnapshot = require('chai-jest-snapshot');

chai.use(chaiJestSnapshot);

beforeEach(function() {
    chaiJestSnapshot.configureUsingMochaContext(this);
});

describe('transformTemplateToJsx', () => {
    before(function() {
        chaiJestSnapshot.resetSnapshotRegistry();
    });
    const makeTest = (templateName, templateContent) => {
        const output = transformTemplateToJsx(templateName, templateContent);
        chai.expect(output).to.matchSnapshot();
    };
    it('should do nothing if no fillers', () => {
        makeTest('abacaba', '<span class="afisha-event-film__content"></span>');
    });
    it('should return fragment', () => {
        makeTest('abacaba', `<div class="stream-channels-list__categories"></div>
             <div class="stream-channels-list__content"></div>`);
    });
    it('should modify filler', () => {
        makeTest('abacaba', `<span class="afisha-event-film__content">
                [% data:content %]
            </span>`);
    });
    it('should modify several execView filler', () => {
        makeTest('abacaba',
            `<div class="answers__card-inner media-service__bg media-service__shadow">
                [% exec:answers__card-question %]
                [% exec:answers__card-answer %]
                [% exec:answers__card-footer %]
            </div>`);
    });
    it('should modify fillers with dot in property', () => {
        makeTest('abacaba',
            `<div class="b-skin-bg b-skin-bg_newspring b-skin-bg_step_[% req:skin.step %]">
                <div class="b-newspring-bg-image"></div>
                <div class="b-newspring-bike"></div>
                [% req:skin.decor %]
            </div>`);
    });
    it('should modify with bem filler', () => {
        makeTest('abacaba',
            `
            <span class="afisha-event-show__inner [% data:innerMix %]">
                <span class="afisha-event-show__image [% data:imageMix %]" [% bem:imageAttrs.attrs %]></span>
                [% data:price %]
                <span class="afisha-event-show__content">
                    <span class="afisha-event-show__text">
                        [% data:content %]
                    </span>
                    [% data:dates %]
                </span>
            </span>
        `);
    });
    it('should modify without obvious source', () => {
        makeTest('abacaba',
            '<h1 class="a11y-hidden">[% label %]</h1>');
    });
    it('should modify translation', () => {
        makeTest('desk-notif-card__points-confirm_screen_big-layout', `
        <div class="[% bem:desk-notif-card__points-screen.class %]">
            <div class="desk-notif-card__points-question">
                [% l10n:traffic.personal.confirm %]
            </div>
            [% data:confirm-button %][% data:reject-button %]
        </div>`);
    });
    it('should modify bem classes', () => {
        makeTest('desk-notif-card__points-confirm_screen_big-layout', `
        <div class="[% bem:desk-notif-card__points-screen.class %]">
            [% data:confirm-link %]
        </div>`);
    });
    it('should modify with cls', () => {
        makeTest('b-banner__adbcontent_iframe', `
        [% b-banner__adbcontent_style_iframe %]
        <div class="[% cls.banner__parent %]">
            [% exec:antiadb__treernd %]
            <div class="[% cls.banner__content %]">[% exec:antiadb__treernd %]</div>
            [% exec:antiadb__treernd %]
        </div>`);
    });
    it('should be failed with scripts', () => { // fixme
        makeTest('b-banner__jsonapi_script', `
            var bannerData=[% data:banner %],
            bannerElem=document.querySelectorAll('.[% cls:b-banner__wrap %]')[0];
            AwapsJsonAPI.Json.prototype.drawBanner(bannerElem, bannerData);
            AwapsJsonAPI.Json.prototype.expand(bannerData);
        `);
    });
    it('should be failed with attributes as a string', () => {
        makeTest('b-banner__adbcontent_iframe', `
        <style [% exec:csp-nonce %]>
            @media screen and (max-width: [% minWidth %]px) {.banner__expand .banner__expand_inner {display: none;}}
        </style>`);
    });
    it('should modify with inline styles', () => {
        makeTest('b-banner__adbcontent_iframe', `
        <style>
            .[% cls.banner__parent %]{
                position:relative;
                width:[% sizernd.width %];
                height:[% sizernd.height %];
                margin:0 0 18px 20px;
            }
            .[% cls.banner__size %]{
                width:[% sizernd.width %];
                height:[% sizernd.height %];
                margin:0;
                display:block;
                border:none;
            }
        </style>`);
    });
    it('should replace fillers inside string appropriately', () => {
        makeTest('abacaba', "'[% data:content %]'");
    });
    it('should work with bem:js', () => {
        makeTest('stream-inserts-mix', `
        <div class="[% bem:stream-inserts-mix.class %]" [% bem:attrs %] data-bem="[% bem:js %]">
    <div class="stream-inserts-mix__left">
        [% data:dataLeft %]
    </div>
    <div class="stream-inserts-mix__center">
        [% data:dataCenter %]
    </div>
    <div class="stream-inserts-mix__right">
        [% data:dataRight %]
    </div>
</div>`);
    });
    it('should modify self closing tags appropriately', () => {
        makeTest('abacaba', '<img src="//yastatic.net/weather/i/icons/funky/dark/48/[% data:icon %].png" alt="">');
    });
    it('bem:headerMods.media-service__header', () => {
        makeTest('media-service__layout', `
            <div className="[% bem:headerMods.media-service__header.class %]">
                [% data:header %]
                [% data:title-after %]
                [% data:more %]
            </div>
        `);
    });
    it('attribute in inappropriate place', () => {
        makeTest('abacaba', `
            [% exec:doctype %]
            <html [% document__mod %][% document__lang %]>
                <head xmlns:og="http://ogp.me/ns#">
                    [% head__content %]
                    [% resources__head %]
                </head>
                [% body %]
            </html>
        `);
    });
    it('name=[% name %]', () => {
        makeTest('abacaba', `
        <input name=[% name %] type="hidden" value="[% value %]">
        `);
    });
    it('b-banner__img', () => {
        makeTest('b-banner__img', '<img [% bem:attrs %]>');
    });
    it('exec inside attribute', () => {
        makeTest('abacaba', `
            <div class="logo__image_no_bg">
              <img src="[% exec:logo__url %]" [% exec:logo__content__attrs %]/>
              <script[% exec:csp-nonce %]>[% data:fallback %]</script>
            </div>
        `);
    });
    it('exec inside attribute 2', () => {
        makeTest('body__layout', `
            <style[% exec:csp-nonce %]>
            .b-page{display:none}
            </style>
        `);
    });
    it('list__layout', () => {
        makeTest('body__layout', `
        <[% tag %] class="[% bem:list.class %]">[% content %]</[% tag %]>
    `);
    });
    it('two fillers', () => {
        makeTest('abacabaabacaba', `
            [% exec:card__title %]
            [% exec:card__subtitle %]
    `);
    });
    it('plain string modifying', () => {
        makeTest('abacabaabacaba', `
            abacabaabacaba
    `);
    });
    it('should format values correctly', () => {
        makeTest('traffic', '<div class="traffic__map-link"><img class="traffic__map" src="https://[% data:src %]" width="[% data:width %]" height="[% data:height %]" alt=""></div>');
    });
});
