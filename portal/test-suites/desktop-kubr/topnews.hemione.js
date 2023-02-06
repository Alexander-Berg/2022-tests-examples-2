'use strict';

specs('topnews', function () {
    it.skip('Персональные', async function () {
        var tab = '#news_tab_personal[data-key="personal"]';

        await this.browser.yaOpenMorda({getParams: {gramps: 1}});
        await this.browser.$('.auth__username .input__input').then(elem => elem.setValue('alexanderovechkintest'));
        await this.browser.$('.auth__password .input__input').then(elem => elem.setValue('Sx4-N3A-4M8-JZu'));
        await this.browser.keys('Enter');
        await this.browser.yaWaitUrl({host: 'mail.yandex.ru'});

        await this.browser.yaOpenMorda({getParams: {}, expectations: {
            ignoreErrorsSource: /network/,
            ignoreErrorsMessage: /(mail.yandex.ru)|(mc.yandex.ru)/
        }});

        const username = await this.browser.$('.username').then(elem => elem.isExisting());
        if (!username) {
            await this.yaReload();
        }

        await this.browser.yaGeometry(({expect}) => {
            expect('.username').to.exist();
            expect(tab).to.exist()
                .and.to.be.visible();
        });
    });
});
