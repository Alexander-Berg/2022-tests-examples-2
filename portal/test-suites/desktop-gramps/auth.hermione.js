'use strict';

specs('auth', function () {
    it('Авторизация', async function() {
        await this.browser.yaOpenMorda({getParams: {gramps: 1}});
        {
            const status = await this.browser.yaGetLoginStatus();
            status.should.equal(false);
        }

        await this.browser.$('.auth__username .input__input').then(elem => elem.setValue('morda-hermione'));
        await this.browser.assertView('login', '.domik2__dropdown');

        await this.browser.$('.auth__password .input__input').then(
            elem => elem.setValue(require('../../../tools/get_secret')('hermione-user', 'password'))
        );

        await this.browser.assertView('password', '.domik2__dropdown');
        await this.browser.keys('Enter');
        await this.browser.yaWaitUrl({host: 'mail.yandex.ru'});

        // network log ловит ошибки с почты
        await this.browser.yaOpenMorda({getParams: {gramps: 1}, expectations: {
            ignoreErrorsSource: /network/,
            // https://st.yandex-team.ru/HOME-51187
            ignoreErrorsMessage: /(mail.yandex.ru)|(mc.yandex.ru)/
        }});

        {
            const status = await this.browser.yaGetLoginStatus();
            status.should.equal(true);
        }
        await this.browser.yaHideElement('.username');
        await this.browser.yaHideElement('.domik2__dropdown-notification:nth-child(2) .domik2__notification-info');
        await this.browser.assertView('logged', '.domik2__dropdown');
    });
});
