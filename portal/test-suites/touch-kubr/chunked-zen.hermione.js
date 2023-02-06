'use strict';

specs('chunked zen', function () {
    const ZEN_FLAGS = [
        'zen_chunked_feed_news_nopin',
        'zen_touch_infinity',
        'zen_touch_infinity_7',
        'touch_redesign_new',
        'zen_touch_infinity',
        'topnews_extended'
    ].join(':');

    [
        'yandex.ru'
        /* TODO включить, когда в hermione-auth-commands добавят не-ru
        * https://st.yandex-team.ru/INFRADUTY-17803
        'yandex.by',
        'yandex.uz'
        */
    ].map(domain => {
        describe(domain, function () {
            describe('дзен включен', function () {
                beforeEach(async function () {
                    await this.browser.yaOpenMorda({
                        getParams: {
                            ab_flags: ZEN_FLAGS
                        },
                        zone: domain.replace('yandex.', ''),
                        expectations: {
                            ignoreErrorsMessage: /(strm\.yandex\.ru|static-maps\.tst\.maps\.yandex\.ru)/
                        }
                    });
                });

                it('дзен приходит в html и нет клиентских ошибок', async function () {
                    const source = await this.browser.getPageSource();
                    if (source.indexOf('<div id="zen">') === -1) {
                        throw new Error(`ЧЗ не включился: '...${source.substr(-5000)}'`);
                    }
                });

                it('дзен имеет правильные размеры и положение', async function () {
                    await this.browser.$('.zen-app .touch-feed').then(elem => elem.waitForExist());
                    await this.browser.yaGeometry(({expect}) => {
                        expect('.zen-app').to.be.containedIn('.infinity-zen')
                            .and.to.be.under('.content__informers-bg');

                        expect('.zen-app .touch-feed')
                            .to.not.have.width(0);
                    });
                });

                it.skip('при проблемах с клиентсайдом дзена на странице остаются вставки', function () {
                    // TODO дописать тест после обновления гермионы
                });

                it('в фиде есть вставки', async function () {
                    /* здесь вставки любые - и серверсайд и клиентсайд */
                    await this.browser.yaInBrowser(async () => {
                        const INSERTS_COUNT = 2;
                        let scroll = window.scrollY;
                        let insert;
                        do {
                            insert = document.querySelectorAll('.zen-lib__container .block[data-bem]');
                            if (insert.length < INSERTS_COUNT) {
                                scroll += window.innerHeight * 0.8;
                                window.scrollTo(0, scroll);
                                await new Promise(resolve => setTimeout(resolve, 100));
                            }
                        } while (insert.length < INSERTS_COUNT && scroll < window.innerHeight * 30);
                        if (insert.length < INSERTS_COUNT) {
                            throw new Error(`нашлось ${insert.length} из ${INSERTS_COUNT} вставок при скролле до ${scroll}`);
                        }
                    });
                });

                it('новости в первой пачке', async function () {
                    await this.browser.yaGeometry(({expectFirstOf}) => {
                        expectFirstOf('.news').to.exist()
                            .and.to.be.visible();
                    });
                });

                it('в стейте дзена есть вставки', async function () {
                    const INSERTS_COUNT = 4;
                    const names = await this.browser.yaInBrowser(() => {
                        const inserts = window.YandexZen.state.inserts;
                        const items = inserts && inserts.Insert || [];

                        return items.map(item => item.name);
                    });

                    if (names.length < INSERTS_COUNT) {
                        throw new Error(`нашлось ${names.length} из ${INSERTS_COUNT} вставок в стейте дзена: ${names.join(', ')}`);
                    }
                });
            });

            describe('дзен выключен', function () {
                beforeEach(async function () {
                    const tld = domain.replace('yandex.', '');
                    await this.browser.yaOpenMorda({
                        zone: tld,
                        path: '/empty.html'
                    });
                    try {
                        await this.browser.authAny('disabled-zen');
                    } catch (e) {
                        e.message = `не удалось залогиниться: ${e.message}`;
                        throw e;
                    }

                    try {
                        const retpath = await this.browser.yaGetMordaUrl({
                            zone: tld,
                            path: '/empty.html'
                        });
                        const tuneUrl = `https://yandex.${tld}/tune/common?retpath=${retpath}`;

                        await this.browser.url(tuneUrl);

                        const zenToggler = 'input[name=yes_touch_infinity_zen]';
                        await this.browser.yaGeometry(({expectFirstOf}) => {
                            expectFirstOf(zenToggler)
                                .to.exist()
                                .and.not.to.have.attribute('disabled');
                        });

                        const checked = await this.browser.$(zenToggler).then(elem => elem.getAttribute('checked'));
                        if (checked) {
                            // выключение настройки
                            await this.browser.$(zenToggler).then(elem => elem.click());
                            await this.browser.$('.form__save').then(elem => elem.click());
                        }

                        await this.browser.yaCheckLog();
                    } catch (e) {
                        e.message = `Не удалось выключить дзен в тюне: ${e.message}`;
                        throw e;
                    }

                    // Небольшая задержка, чтобы датасинк точно успел записать
                    await new Promise(resolve => setTimeout(resolve, 100));

                    await this.browser.yaOpenMorda({
                        getParams: {
                            ab_flags: ZEN_FLAGS
                        },
                        zone: tld,
                        expectations: {
                            ignoreErrorsMessage: /(strm\.yandex\.ru|static-maps\.tst\.maps\.yandex\.ru)/
                        }
                    });
                });
                afterEach(async function() {
                    await this.browser.unlockAccount();
                });

                it('дзена нет на странице', async function () {
                    if (await this.browser.$('.zen-app').then(elem => elem.isExisting())) {
                        await this.browser.$('.zen-app').then(elem => elem.scrollIntoView());
                    }
                    await this.browser.yaGeometry(({expect}) => {
                        expect('.zen-app').to.not.exist();
                    });
                });

                it('новости и другие блоки есть на странице', async function () {
                    await this.browser.yaGeometry(({expectFirstOf, expectAnyOf}) => {
                        expectFirstOf('.news').to.exist()
                            .and.to.be.visible();
                        expectAnyOf('.news ~ .block').to.exist();
                    });
                });
            });
        });
    });
});
