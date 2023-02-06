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
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif1.TouchButtonReadAll()).click();
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
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif1.TouchButtonDeleteAll()).then(async elem => {
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
                await this.browser.$(this.PO.NotificationPile.forServiceID('fakeservice2').Trigger()).then(async elem => {
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
                    await this.browser.yaWaitForPileAnimation('collapse');
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
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif1.TouchButtonDelete()).then(async elem => {
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
                await this.browser.swipeLeft(notifL.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notifL.TouchButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForNotificationAnimation('delete', pile);
                });
                await this.browser.yaAssertViewport('last-delete');
            });

            it('Удалить среднее уведомление', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice2');
                const notifL = pile.NotifWrap.forId('rcnt6');
                await this.browser.swipeLeft(notifL.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notifL.TouchButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForNotificationAnimation('delete');
                });
                await this.browser.yaAssertViewport('last-delete');
            });
        });

        describe('Стопка из 2 уведомлений', function() {
            this.beforeEach(async function() {
                await this.browser.openFrame('/gnc/frame?exp_flags=tabs=0;groups=1&fixture=group-two');
                await this.browser.yaAssertViewport('inited');
                await this.browser.$(this.PO.NotificationPile.forServiceID('fakeservice1').Trigger()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('expand');
                });
                await this.browser.yaAssertViewport('opened');
            });

            it('Удаление первого уведомления', async function() {
                const notif1 = this.PO.NotificationPile.forServiceID('fakeservice1').NotifWrap.forId('rcnt0');
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif1.TouchButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('deleted');
            });

            it('Удаление второго уведомления', async function() {
                const notif2 = this.PO.NotificationPile.forServiceID('fakeservice1').NotifWrap.forId('rcnt1');
                await this.browser.swipeLeft(notif2.Slider(), 150, 20);
                // await this.browser.swipeLeft(notif2.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif2.TouchButtonDelete()).then(async elem => {
                    elem.click();
                    await this.browser.yaWaitForPileAnimation('collapse');
                });
                await this.browser.yaAssertViewport('deleted');
            });

            it('Прочтение первого уведомления', async function() {
                const notif1 = this.PO.NotificationPile.forServiceID('fakeservice1').NotifWrap.forId('rcnt0');
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif1.TouchButtonRead()).click();
                await this.browser.yaAssertViewport('read');
            });

            it('Прочтение второго уведомления', async function() {
                const notif2 = this.PO.NotificationPile.forServiceID('fakeservice1').NotifWrap.forId('rcnt1');
                await this.browser.swipeLeft(notif2.Slider(), 150, 20);
                // await this.browser.swipeLeft(notif2.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif2.TouchButtonRead()).click();
                await this.browser.yaAssertViewport('read');
            });

            it('Прочтение первого и второго уведомления', async function() {
                const pile = this.PO.NotificationPile.forServiceID('fakeservice1');
                const notif1 = pile.NotifWrap.forId('rcnt0');
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.swipeLeft(notif1.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped-1');
                await this.browser.$(notif1.TouchButtonRead()).click();
                await this.browser.yaAssertViewport('read-one');
                const notif2 = pile.NotifWrap.forId('rcnt1');
                await this.browser.swipeLeft(notif2.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped-2');
                await this.browser.$(notif2.TouchButtonRead()).click();
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
                await this.browser.swipeLeft(notif.Slider(), 150, 20);
                await this.browser.swipeLeft(notif.Slider(), 150, 20);
                await this.browser.yaAssertViewport('swiped');
                await this.browser.$(notif.TouchButtonReadAll()).click();
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
    });
});
