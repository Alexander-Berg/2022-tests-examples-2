'use strict';

specs('by-region', function () {
    it('Открывает морду в Минске', async function() {
        await this.browser.yaOpenMorda({
            zone: 'by',
            dump: true,
            getParams: {
                ab_flags: 'touch_redesign_new',
                redirect: 0
            }
        });
        {
            const country = await this.browser.yaGetDumpValue('country_id');
            country.should.equal('149');
        }

        await this.browser.$('.user-profile__avatar').then(elem => elem.click());
        await this.browser.$('.user-profile__settings').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: /tune/});
        await this.browser.$('.index-options .link').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: /geo/});
        await this.browser.yaIgnoreElement('.geo-map');
        await this.browser.$('.city__input .input__input').then(elem => elem.setValue('гомель'));

        await this.browser.waitUntil(() => {
            return this.browser.execute(function () {
                return $('.b-autocomplete-item__span:contains(Беларусь)').length > 0;
            });
        });

        await this.browser.$('.b-autocomplete-item').then(elem => elem.waitForDisplayed());

        // .touch('.b-autocomplete-item')
        // Клик js'ом, так как попап ловит touchstart, которого в нашем браузере нет и скрывается, кликнуть нельзя
        await this.browser.yaJSClick('.b-autocomplete-item');

        await this.browser.yaWaitUrl({pathname: '/', zone: 'by'});

        // TODO Проблемы CSP на tune, уже почти исправлено
        await this.browser.yaOpenMorda({
            zone: 'by',
            dump: true,
            expectations: {ignoreErrorsSource: /security/},
            getParams: {
                ab_flags: 'touch_redesign_new',
                redirect: 0
            }
        });

        {
            const country = await this.browser.yaGetDumpValue('country_id');
            country.should.equal('149');
            const gid = await this.browser.yaGetCookieValue('yandex_gid');
            gid.should.equal('155');
            const ygu = await this.browser.yaGetYpCookie('ygu');
            ygu.should.equal('0');
        }

        await this.browser.$('.user-profile__avatar').then(elem => elem.click());
        await this.browser.$('.user-profile__settings').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: /tune/});
        await this.browser.$('.index-options .link').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: /geo/});
        await this.browser.$('.checkbox').then(elem => elem.click());
        await this.browser.$('.form__save').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: '/', zone: 'ru'});

        const ygu = await this.browser.yaGetYpCookie('ygu');
        ygu.should.equal('1');
    });
});
