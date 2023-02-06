'use strict';

specs('chunked zen', function () {
    const ZEN_FLAGS = [
        'zen_no_shadow',
        'filter_blocks_big'
    ].join(':');

    [
        'yandex.ru',
        'yandex.by',
        'yandex.kz'
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
                            // TODO убрать, когда дзен прочинит хамстер ZEN-57283
                            ignoreKeywords: ['undefined']
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
                    await this.browser.$('.zen-page .feed').then(elem => elem.waitForExist());
                    await this.browser.yaGeometry(({expect}) => {
                        expect('.zen-app').to.be.containedIn('.infinity-zen')
                            .and.to.be.under('.container__search')
                            .and.to.have.width(918);

                        expect('.zen-page .feed')
                            .to.not.have.width(0);
                    });
                });

                it.skip('при проблемах с клиентсайдом дзена на странице остаются вставки', function () {
                    // TODO дописать тест после обновления гермионы
                });

                if (domain !== 'yandex.uz') {
                    it('в фиде есть вставки', async function () {
                        const zen = await this.browser.$('.zen-app').then(elem => elem.isExisting());
                        if (!zen) {
                            throw new Error('Дзена нет');
                        }
                        /* здесь вставки любые - и серверсайд и клиентсайд */
                        await this.browser.yaInBrowser(async () => {
                            const INSERTS_COUNT = 1;
                            let scroll = window.scrollY;
                            let insert;
                            do {
                                insert = document.querySelectorAll('.zen-lib__container .zen-insert-block');
                                if (insert.length < INSERTS_COUNT) {
                                    scroll += window.innerHeight * 0.8;
                                    window.scrollTo(0, scroll);
                                    await new Promise(resolve => setTimeout(resolve, 100));
                                }
                            } while (insert.length < INSERTS_COUNT && scroll < window.innerHeight * 30);
                            if (insert.length < INSERTS_COUNT) {
                                throw new Error(`нашлось ${insert.length} из ${INSERTS_COUNT} вставки при скролле до ${scroll}`);
                            }
                        });
                    });

                    it('в стейте дзена есть вставки', async function () {
                        const INSERTS_COUNT = domain === 'yandex.ru' ? 3 : 1;
                        const names = await this.browser.yaInBrowser(() => {
                            const inserts = window.YandexZen.state.inserts;
                            const items = inserts && inserts.Insert || [];

                            return items.map(item => item.name);
                        });

                        if (names.length < INSERTS_COUNT) {
                            throw new Error(`нашлось ${names.length} из ${INSERTS_COUNT} вставок в стейте дзена: ${names.join(', ')}`);
                        }
                    });
                }
            });

            describe('дзен выключен', function () {
                beforeEach(async function () {
                    const url = await this.browser.yaGetMordaUrl({
                        zone: domain.replace('yandex.', '')
                    });

                    await this.browser.url(url);

                    const foldUrl = await this.browser.yaInBrowser(() => {
                        try {
                            return home.export['media-grid'].blocks_fold_url;
                        } catch (e) {
                            e.message = 'Не удалось получить урл сохранения настройки: ' + e.message;
                            throw e;
                        }
                    });
                    if (!foldUrl) {
                        throw new Error('Урл сохранения настроек не правильный');
                    }
                    await this.browser.url(foldUrl + 'infinity_zen');
                    await this.browser.yaOpenMorda({
                        getParams: {
                            ab_flags: ZEN_FLAGS
                        },
                        zone: domain.replace('yandex.', '')
                    });
                });

                it('дзена нет на странице', async function () {
                    await this.browser.yaGeometry(({expect}) => {
                        expect('.zen-app').to.not.exist();
                        expect('.media-grid .media-service').to.exist()
                            .and.to.be.visible();
                    });
                });
            });
        });
    });
});
