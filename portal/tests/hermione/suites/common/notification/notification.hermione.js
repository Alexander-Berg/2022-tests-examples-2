describe('Редизайн', function() {
    describe('Уведомление', function() {
        for (const [name, fixture] of [
            ['Просто текст', 'n-text'],
            ['Старое уведомление', 'n-old'],
            ['Уведомление прочитано', 'n-read'],
            ['Уведомление с превью', 'n-preview'],
            ['Уведомление с превью прочитано', 'n-read-preview'],
            ['Уведомление с аватаром', 'n-avatar'],
            ['Уведомление с аватаром прочитано', 'n-read-avatar'],
        ]) {
            it(name, async function() {
                await this.browser.openFrame({
                    fixture,
                    expFlags: {
                        groups: 0,
                        tabs: 0,
                    },
                });
                await this.browser.yaAssertViewport('inited');
            });
        }
    });
    describe('Вкладки', function() {
        it('Нет важных', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=1;groups=0&fixture=rich-fixed-time');
            await this.browser.yaAssertViewport('rich');
        });

        it('Есть важные', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=1;groups=0&fixture=i-mixed');
            await this.browser.yaAssertViewport('important');
        });

        it('Только важные', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=1;groups=0&fixture=important-only');
            await this.browser.yaAssertViewport('important-only');
        });

        it('Переключение вкладок', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=1;groups=0&fixture=i-mixed');
            await this.browser.yaAssertViewport('important');
            const services = await this.browser.$(this.PO.Notifications.servicesTab());
            await services.click();
            await this.browser.yaAssertViewport('services');
        });

        it('Нет вкладок', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=1;groups=0&fixture=empty');
            await this.browser.yaAssertViewport('no-tabs');
        });
    });

    describe('Группы', function() {
        describe('Важные случаи', function() {
            it('Первое уведомление уже прочитано', async function() {
                await this.browser.openFrame({
                    fixture: 'i-first-read',
                    expFlags: {
                        tabs: 0,
                        groups: 1,
                    },
                });
                await this.browser.yaAssertViewport('already-read');
            });
            for (const [title, fixture] of [
                ['Аватар у первого уведомления', 'g-avatar-1'],
                ['Превью у первого уведомления', 'g-preview-1'],
                ['Нет скачка текста без превью', 'g-text-1'],
            ]) {
                it(title, async function() {
                    await this.browser.openFrame({
                        fixture,
                        expFlags: {
                            tabs: 0,
                            groups: 1,
                        }
                    });
                    await this.browser.yaAssertViewport('collapse');
                    await this.browser.$(this.PO.NotificationPile.Trigger()).then(async elem => {
                        elem.click();
                        await this.browser.yaWaitForPileAnimation('expand');
                    });
                    await this.browser.yaAssertViewport('expand');
                });
            }
        });

        it('Нет групп', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-none');
            await this.browser.yaAssertViewport('group-none');
        });

        it('Есть группы', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group');
            await this.browser.yaAssertViewport('group');
        });
        it('Раскрытие группы', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-open-close');
            await await this.browser.$(this.PO.NotificationPile.Trigger()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await this.browser.yaAssertViewport('group-open');
        });
        it('Закрытие группы', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-open-close');
            await await this.browser.$(this.PO.NotificationPile.Trigger()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await await this.browser.$(this.PO.NotificationPile.Header.ButtonCollapse()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('collapse');
            });
            await this.browser.yaAssertViewport('group-close');
        });

        it('Показать ещё', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-show-more');
            await this.browser.yaAssertViewport('inited');
            const pile1 = this.PO.NotificationPile.forServiceID('fakeservice');
            const pile2 = this.PO.NotificationPile.forServiceID('fakeservice2');

            await this.browser.$(pile1.Trigger()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await this.browser.yaAssertViewport('first-open');

            await this.browser.$(pile2.Trigger()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await this.browser.yaAssertViewport('second-open');

            await this.browser.$(pile1.ShowMore()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await this.browser.$(pile1.ShowMore()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
        });
    });
    describe('Вкладки: Эксперименты', function() {
        it('Важное без групп', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=groups=1;tabs=1;important_no_groups=1&fixture=two-services');
            await this.browser.yaAssertViewport('no-groups');
            const services = await this.browser.$(this.PO.Notifications.servicesTab());
            await services.click();
            await this.browser.yaAssertViewport('services');
        });

        it('Один сервис без групп', async function() {
            await this.browser.openFrame('/gnc/frame?exp_flags=groups=1;tabs=1;single_service_no_groups=1&fixture=one-service');
            await this.browser.yaAssertViewport('no-groups');
            const services = await this.browser.$(this.PO.Notifications.servicesTab());
            await services.click();
            await this.browser.yaAssertViewport('no-groups-services');
        });
    });
});
