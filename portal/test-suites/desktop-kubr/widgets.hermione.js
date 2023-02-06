'use strict';

specs('widgets', function () {
    // Перед каждым тестом удаляем виджетную куку
    async function clearWidgets() {
        await this.browser.setWindowSize(1400, 1080);

        await this.browser.yaOpenMorda({
            path: '/empty.html'
        });

        await this.browser.deleteCookies('wd');
        await this.browser.deleteCookies('wp');
        await this.browser.deleteCookies('w');
        return this.browser.yaSetRegion(213, {reload: false});
    }

    beforeEach(clearWidgets);

    it('Должно cохранять настройки', async function () {
        const tab = '.news .news__head-item [data-key=custom]';
        await this.browser.yaOpenMorda();
        await this.browser.yaHover('.widget_id_topnews-1');
        await this.browser.$('.widget_id_topnews-1 .widget-control__button').then(elem => elem.click());
        await this.browser.$('.menu__icon_glyph_settings').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: '/'});

        // Ждём загрузки формы внутри попапа
        await this.browser.$('.b-wdgt-preferences__data').then(elem => elem.waitForDisplayed());

        await this.browser.$('.b-wdgt-preferences__pref .select__button').then(elem => elem.click());
        await this.browser.$('.select__popup .select__item:not(.select__item_selected_yes):last-child').then(elem => elem.click());
        await this.browser.$('.b-wdgt-preferences__save').then(elem => elem.click());
        await this.browser.yaWaitUrl({pathname: '/'});

        const exist = await this.browser.$(tab).then(elem => elem.isExisting());
        if (!exist) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            await this.browser.yaReload();
        }

        await this.browser.yaGeometry(({expect}) => {
            expect(tab)
                .to.exist()
                .and.to.be.visible();
        });
    });

    describe.skip('Отдельные виджеты', function () {
        beforeEach(clearWidgets);

        const testWidgets = [{
            name: 'новости',
            id: '_topnews',
            ignore: '.news__head-item:not(h1), .news__panels, .inline-stocks',
            savedSelector: '.widget_name_topnews'
        }, {
            name: 'котировки',
            id: '_stocks',
            ignore: '.stocks .head, .stocks td:nth-child(n + 2)',
            savedSelector: '.widget_name_stocks:not(.widget_empty_yes)'
        }, {
            name: 'rss-произвольный',
            id: '234',
            ignore: '.w-rss',
            savedSelector: '.widget_name_234'
        }, {
            name: 'rss-новости',
            id: '_rssnews',
            ignore: '.w-rssnews .news',
            savedSelector: '.widget_name_rssnews'
        }];

        for (const widget of testWidgets) {
            it(`Добавляет виджет и он работает: ${widget.name}`, async function() {
                await this.browser.setWindowSize(1024, 4096);

                // Открываем морду с добавлением виджета
                await this.browser.yaOpenMorda({
                    getParams: {
                        add: widget.id
                    },
                    expectations: {
                        ignoreErrorsMessage: /WidgetApi_no_jquery\.js/
                    }
                });

                await this.browser.pause(5000);

                await this.browser.yaOpenMorda();

                await this.browser.$('.zen-lib_state_loaded').then(elem => elem.waitForDisplayed());
                await this.browser.$(widget.savedSelector).then(elem => elem.waitForDisplayed());
                await this.browser.yaHideElement(widget.ignore);

                await this.browser.execute(function () {
                    var tabs = document.querySelector('.news__tabs');
                    if (tabs) {
                        var elems = tabs.childNodes;
                        for (var i = 0; i < elems.length; ++i) {
                            if (elems[i].nodeValue === ' ') {
                                elems[i].parentNode.removeChild(elems[i]);
                            }
                        }
                    }
                });

                // Проверяем, что после перезагрузки виджет правильный
                await this.browser.assertView('saved-widget', widget.savedSelector);

                await this.browser.yaHover(widget.savedSelector);

                // Скриншотим виджет с шестерёнкой
                await this.browser.assertView('control-hovered', widget.savedSelector);

                await this.browser.$(widget.savedSelector + ' .widget-control__button').then(elem => elem.click());
                await this.browser.$('.menu__icon_glyph_settings').then(elem => elem.click());

                // Ждём загрузки формы внутри попапа
                await this.browser.$('.b-wdgt-preferences__data').then(elem => elem.waitForDisplayed());

                await this.browser.yaHover('.b-wdgt-preferences__save');

                await this.browser.execute(function () {
                    $('.multiselect').css('overflow', 'hidden');
                });

                await this.browser.assertView('settings', '.b-wdgt-preferences .popup__content');
            });
        }
    });
});
