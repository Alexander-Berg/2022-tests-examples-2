describe('Редизайн', function() {
    describe('Группы', function() {
        describe('Группа закрыта', function() {
            this.beforeEach(async function() {
                await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-read');
                await this.browser.yaAssertViewport('inited');
            });

            it('Прочитать все', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                const notif1 = pile.NotifWrap.forId('rcnt4');
                await this.browser.$(notif1.DesktopButtonReadAll()).click();
                await this.browser.yaAssertViewport('read-all-collapsed');
                await this.browser.$(pile.Trigger()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('read-all');
            });

            it('Удалить все', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                const notif1 = pile.NotifWrap.forId('rcnt4');
                await this.browser.$(notif1.DesktopButtonDeleteAll()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('delete');
                });
                await this.browser.yaAssertViewport('delete-all');
            });
        });

        describe('Группа раскрыта', function() {
            this.beforeEach(async function() {
                await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-read');
                await this.browser.yaAssertViewport('inited');
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                await this.browser.$(pile.Trigger()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('opened');
            });
            it('Прочитать все', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                await this.browser.$(pile.Header.ButtonReadAll()).click();
                await this.browser.yaAssertViewport('all-read');
                await this.browser.$(pile.Header.ButtonCollapse()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('all-read-collapsed');
            });

            it('Удалить все', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                await this.browser.$(pile.Header.ButtonDeleteAll()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('delete');
                });
                await this.browser.yaAssertViewport('all-read-collapsed');
            });

            it('Удалить первое уведомление', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                const notif1 = pile.NotifWrap.forId('rcnt4');
                await this.browser.$(notif1.DesktopButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForNotificationAnimation('delete', pile);
                });
                await this.browser.yaAssertViewport('first-delete');
                await this.browser.$(pile.Header.ButtonCollapse()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('first-delete-collapsed');
            });

            it('Удалить последнее уведомление', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                const notifL = pile.NotifWrap.forId('rcnt8');
                await this.browser.$(notifL.DesktopButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForNotificationAnimation('delete', pile);
                });
                await this.browser.yaAssertViewport('last-delete');
            });

            it('Удалить среднее уведомление', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                const notifL = pile.NotifWrap.forId('rcnt6');
                await this.browser.$(notifL.DesktopButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForNotificationAnimation('delete', pile);
                });
                await this.browser.yaAssertViewport('last-delete');
            });
        });

        describe('Стопка из 2 уведомлений', function() {
            this.beforeEach(async function() {
                await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-two');
                await this.browser.yaAssertViewport('inited');
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.Trigger()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('opened');
            });

            it('Удаление первого уведомления', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.NotifWrap.forId('rcnt0').DesktopButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('deleted');
            });

            it('Удаление второго уведомления', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.NotifWrap.forId('rcnt1').DesktopButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('deleted');
            });

            it('Прочтение первого уведомления', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.NotifWrap.forId('rcnt0').DesktopButtonRead()).click();
                await this.browser.yaAssertViewport('read');
            });

            it('Прочтение второго уведомления', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.NotifWrap.forId('rcnt1').DesktopButtonRead()).click();
                await this.browser.yaAssertViewport('read');
            });

            it('Прочтение первого и второго уведомления', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                const notif1 = pile.NotifWrap.forId('rcnt0');
                await this.browser.$(notif1.DesktopButtonRead()).click();
                await this.browser.yaAssertViewport('read-one');
                const notif2 = pile.NotifWrap.forId('rcnt1');
                await this.browser.$(notif2.DesktopButtonRead()).click();
                await this.browser.yaAssertViewport('read-all');
                await this.browser.$(pile.Header.ButtonCollapse()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('read-all-collapsed');
            });

            it('Прочтение первого и второго уведомления 2', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                const notif = pile.NotifWrap.forId('rcnt0');
                await this.browser.$(pile.Header.ButtonCollapse()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.$(notif.DesktopButtonReadAll()).click();
                await this.browser.yaAssertViewport('read-all-collapsed');
                await this.browser.$(pile.Trigger()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('read-all');
            });

            it('Прочтение первого и второго уведомления 3', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.Header.ButtonReadAll()).click();
                await this.browser.yaAssertViewport('read-all');
                await this.browser.$(pile.Header.ButtonCollapse()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('read-all-collapsed');
            });

            it('Удаление стопки', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                await this.browser.$(pile.Header.ButtonDeleteAll()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('delete');
                });
                await this.browser.yaAssertViewport('delete-all');
            });
        });
        for (const id of [5, 6, 12]) {
            it(`Удаление в группе из ${id}-ти уведомлений`, async function() {
                await this.browser.openFrame({
                    fixture: `g-${id}`,
                    expFlags: {
                        tabs: 0,
                        groups: 1,
                    },
                });
                const pile = this.PO.NotificationPile.forServiceID('fakeservice');
                await this.browser.$(pile.Trigger()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('before-removal');
                const notifN = pile.NotifWrap.forId('rcnt4');
                await this.browser.$(notifN.DesktopButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForNotificationAnimation('delete', pile);
                });
                await this.browser.yaAssertViewport('after-removal');
            });
        }
        it('Удаление в группе из 12-ти уведомлений: 2', async function() {
            await this.browser.openFrame({
                fixture: 'g-12',
                expFlags: {
                    tabs: 0,
                    groups: 1,
                },
            });
            const pile = this.PO.NotificationPile.forServiceID('fakeservice');
            await this.browser.$(pile.Trigger()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await this.browser.$(pile.ShowMore()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForPileAnimation('expand');
            });
            await this.browser.$(pile.ShowMore()).scrollIntoView();
            await this.browser.yaAssertViewport('before-removal');
            const notifN = pile.NotifWrap.forId('rcnt9');
            await this.browser.$(notifN.DesktopButtonDelete()).then(async elem => {
                elem.click();
                await this.browser.yaWaitForNotificationAnimation('delete', pile);
            });
            await this.browser.yaAssertViewport('after-removal');
        });
    });
});
