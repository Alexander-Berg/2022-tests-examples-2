const helpers = require('./help');

jest.mock('./const.js', () => ({
    SUPPORT_PHONE: '\\+7 123 456 78 90',
    forms: {
        1: {
            phone: 'answer_1',
            pageId: 'answer_2',
            orderid: 'OrderId'
        }
    }
}));

describe('webview/helpers/help', () => {
    describe('contentPostRequest', () => {
        const options = {
            pageId: 'forgot',
            support_phone: '+7-343-226-09-66',
            zone_name: 'ekb',
            helpType: 'Yandex',
            appPath: 'taxi-app'
        };

        const response = {
            forms: {
                4730: {
                    answer_choices_13698: 'forgot',
                    answer_short_text_49151: 'ekb',
                    HelpType: 'Yandex',
                    title: 'Забыл вещи в машине',
                    lang: 'ru',
                    'media-type': 'mobile',
                    mobile: 'yes',
                    iframe: 1,
                    service: 'taxi'
                }
            },
            /* eslint-disable max-len */
            content: `
                <main role="main" class="doc-c doc-c-main doc-c-i-bem" doc-data-bem="{&quot;doc-c-main&quot;:{}}">
                    <article role="article" aria-labelledby="ariaid-title1" class="doc-c-article">
                    <h1 class="title topictitle1 doc-c-headers doc-c-headers_mod_h1" id="ariaid-title1" data-help-title="1">Забыл вещи в машине</h1>
                    <div class="body conbody" data-help-text="1">
                        <p class="p">Самый быстрый способ вернуть оставленные вещи  — позвонить водителю. Номер телефона
                            указывается в <a class="xref doc-c-link" href="/help/taxi-app/how-to-use/push.html">Push-уведомлении</a>. Вы также можете
                            в разделе <a class="xref doc-c-link" href="/help/taxi-app/how-to-order/history.html">История поездок</a>:
                             кнопка <span class="ph uicontrol doc-c-uicontrol">Позвонить</span> будет доступна 24 часа
                        </p>
                        <p class="p">Если вам не удалось связаться с водителем, напишите нам через форму или позвоните
                            по номеру +7123123.</p>

                        <div class="doc-c-form doc-c-i-bem" id="4730" data-title-from="Забыл вещи в машине" name="4730" doc-data-bem="{&quot;doc-c-form&quot;:{}}">
                        <iframe class="doc-c-form__iframe" frameborder="0" width="100%" name="4730" src="https://forms.yandex.ru/surveys/4730/?answer_choices_13698=forgot&answer_short_text_49151=ekb&HelpType=Yandex&title=%D0%97%D0%B0%D0%B1%D1%8B%D0%BB%20%D0%B2%D0%B5%D1%89%D0%B8%20%D0%B2%20%D0%BC%D0%B0%D1%88%D0%B8%D0%BD%D0%B5&form_title=&lang=ru&media-type=mobile&iframe=1&mobile=yes&service=taxi&referer=undefined&url=undefined"></iframe></div>

                    </div>
                </article></main>
            `,
            /* eslint-enable max-len */
            html_heads: {
                sources: {
                    meta: {},
                    title: 'Забыл вещи в машине'
                }
            },
            info: {
                props: {
                    isCacheable: false
                }
            }
        };

        test('Должен вернуть объект с полями hasForm, content, title, isCacheable', () => {
            expect(Object.keys(helpers.contentPostRequest(response, options))).toEqual([
                'title',
                'content',
                'hasForm',
                'isCacheable'
            ]);
        });

        test('Если на странице есть форма устанавливает hasForm в true иначе false', () => {
            expect(helpers.contentPostRequest(response, options).hasForm).toEqual(true);

            expect(
                helpers.contentPostRequest(
                    {
                        forms: {},
                        content:
                            '<p class="p">Если вам не удалось связаться с водителем, напишите нам через форму или позвоните по номеру +7123123.</p>',
                        html_heads: {}
                    },
                    options
                ).hasForm
            ).toEqual(false);
        });

        test('Если в props.isCached равно true, должно установить isCached в true', () => {
            expect(
                helpers.contentPostRequest(
                    {
                        forms: {},
                        content: '',
                        html_heads: {},
                        info: {
                            props: {
                                isCacheable: true
                            }
                        }
                    },
                    options
                ).isCacheable
            ).toEqual(true);

            expect(
                helpers.contentPostRequest(
                    {
                        forms: {},
                        content: '',
                        html_heads: {},
                        info: {
                            props: {
                                isCacheable: false
                            }
                        }
                    },
                    options
                ).isCacheable
            ).toEqual(false);
        });

        test('Должен подменить iframe на email', () => {
            const TEXT = 'Write us';
            const EMAIL = 'test@test.com';

            expect(
                helpers.contentPostRequest(response, {
                    ...options,
                    os: 'ios',
                    isInAppBrowser: '1',
                    isIframeSupported: '0',
                    formReplacer: {
                        email: EMAIL,
                        text: TEXT
                    }
                }).content
            ).toContain(`<a target="_blank" href="mailto:${EMAIL}">${TEXT}</a>`);

            expect(
                helpers.contentPostRequest(response, {
                    ...options,
                    os: 'ios',
                    isInAppBrowser: '1',
                    isIframeSupported: '0',
                    formReplacer: {
                        email: EMAIL
                    }
                }).content
            ).not.toContain('<div class="doc-c-form');

            expect(
                helpers.contentPostRequest(response, {
                    ...options,
                    os: 'ios',
                    isInAppBrowser: '1',
                    isIframeSupported: '0'
                }).content
            ).not.toContain('<div class="doc-c-form');
        });

        test('Должен вернуть верный заголовок из меты', () => {
            expect(helpers.contentPostRequest(response, options).title).toEqual('Забыл вещи в машине');
        });
    });
});
