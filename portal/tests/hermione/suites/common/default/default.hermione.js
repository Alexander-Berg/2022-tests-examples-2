describe('Редизайн', function() {
    describe('Настройки', function() {
        this.beforeEach(async function() {
            const { browser: bro, PO } = this;
            await bro.openFrame('/gnc/frame?exp_flags=groups=0;tabs=0&fixture=rich-fixed-time');

            await bro.$(PO.Header.More()).then(item => item.click());

            await bro.$(PO.Header.More.Popup()).then(elem => elem.waitForDisplayed());

            await bro.$(PO.Popup.lastMenuItem()).then(e => e.click());
        });

        it('Настройки открываются', async function() {
            const { browser: bro } = this;

            await bro.yaAssertViewport('Settings-Open');
        });

        it('Настройки закрываются', async function() {
            const { browser: bro, PO } = this;
            await bro.$(PO.Settings.ButtonClose()).click();
            await bro.yaAssertViewport('Settings-Close');
        });

        it('Сервис раскрывается', async function() {
            const { browser: bro, PO } = this;
            const settings = PO.Settings.ForServiceID('fakeservice1');

            await bro.$(settings.SectionControlls()).then(e => e.click());
            await bro.yaAssertViewport('Settings-collapsed');

            await bro.$(settings.SectionControlls()).then(e => e.click());
            await bro.yaAssertViewport('Settings-expanded');
        });

        it('Галочка ставится', async function() {
            const { browser: bro } = this;

            await bro.$('#label-cb-fakeservice-qw3').click();
            await bro.yaAssertViewport('Settings-enabled');

            await bro.$('#label-cb-fakeservice-qw3').click();
            await bro.yaAssertViewport('Settings-disabled');
        });
    });
    describe('Фрейм', function() {
        it('Нет уведомлений', async function() {
            const { browser: bro } = this;
            await bro.openFrame('/gnc/frame?fixture=empty');
            await bro.yaAssertViewport('Empty');
        });
    });
});
